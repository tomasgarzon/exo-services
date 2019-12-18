from django.conf import settings
from django.core.exceptions import ValidationError

from invitation.models import Invitation
from relation.signals_define import signal_user_assigned

# TODO: remove certification_group signals connection
from certification.signals_define import (
    delete_certification_group,
    update_certification_group)

from ..models import Step
from ..signals_define import (
    edit_project_start_date, edit_project_duration_date,
    project_category_changed_signal)
from ..tasks import CreateConversationProjectTask
from ..status_helpers import create_status_updates, clear_updates


def process_status_changed(instance):
    if instance.is_started:
        for team in instance.teams.all():
            for team_member in team.team_members.all():
                try:
                    user = instance.project_manager.user
                except AttributeError:
                    user = instance.created_by
                try:
                    Invitation.objects.filter_by_object(team_member)[0].accept(user)
                except (IndexError, ValidationError):
                    pass


def update_certificates_for_project(project):
    certification_group = project.credentials.first()
    update_certification_group.send(
        sender=project.__class__,
        instance=certification_group,
        user_from=project.created_by,
        group_name='{name} - {location}'.format(
            name=project.name,
            location=project.location),
        description=project.comment,
        course_name=project.name,
        issued_on=project.start)


def post_save_service(sender, instance, created, *args, **kwargs):
    update_fields = kwargs.get('update_fields') or []
    project = instance.project_ptr if hasattr(instance, 'project_ptr') else instance
    if created:
        if instance.customize.get('steps').get('populate'):
            Step.objects.create_steps(instance)
        if instance.created_by:
            project.add_manager_permissions(instance.created_by)
            signal_user_assigned.send(
                sender=sender,
                project=project,
                user=instance.created_by,
            )
            create_status_updates(project)
    else:
        project = instance.project_ptr if hasattr(instance, 'project_ptr') else instance
        if 'start' in update_fields:
            edit_project_start_date.send(
                sender=sender,
                instance=project,
            )

        if 'duration' in update_fields:
            edit_project_duration_date.send(sender=sender, instance=project)
        if settings.ACCREDIBLE_ENABLED and project.credentials.exists():
            update_certificates_for_project(project)

    if 'status' in update_fields:
        process_status_changed(instance)
    if 'category' in update_fields:
        project_category_changed_signal.send(
            sender=sender,
            instance=instance)


def update_start_date(sender, instance, *args, **kwargs):
    """
        Intialize dates for project Steps
    """
    Step.objects.start_steps(instance)


def update_project_status(sender, instance, *args, **kwargs):
    clear_updates(instance)
    create_status_updates(instance)


def update_duration(sender, instance, *args, **kwargs):
    Step.objects.update_steps(instance)


def pre_delete_project(sender, instance, *args, **kwargs):
    project = instance.project_ptr if hasattr(instance, 'project_ptr') else instance
    if settings.ACCREDIBLE_ENABLED:
        delete_certification_group.send(
            sender=instance.__class__,
            instance=project,
        )


def pre_save_project(sender, instance, *args, **kwargs):
    if instance.pk is None:
        type_project = instance.type_verbose_name.upper()
        template_name = settings.PROJECT_TYPE_TO_TEMPLATE.get(type_project)
        instance.template = template_name


def create_external_info_handler(sender, project, user, *args, **kwargs):
    CreateConversationProjectTask().s(
        project_id=project.id,
        user_from_id=user.id).apply_async()
