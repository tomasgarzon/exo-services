from django.conf import settings

from exo_role.models import ExORole
from ecosystem.signals_define import projects_ecosystem_changed

from ..signals_define import (
    signal_head_coach_created,
    signal_head_coach_removed,
    signal_user_assigned,
    signal_user_unassigned
)


def consultant_project_role_post_save(
    sender, instance, created,
    *args, **kwargs
):

    update_fields = kwargs.get('update_fields') or []

    if (created or 'status' in update_fields) and (instance.is_active):
        user = instance.consultant.user

        signal_user_assigned.send(
            sender=sender,
            project=instance.project,
            user=user,
        )
        instance.project.add_permission(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            user,
        )

        if instance.has_manager_perms:
            # send signal
            signal_head_coach_created.send(
                sender=sender,
                relation=instance,
            )
        if instance.exo_role.code == settings.EXO_ROLE_CODE_SPRINT_REPORTER:
            instance.project.add_permission(
                settings.PROJECT_PERMS_ONLY_VIEW_PROJECT,
                instance.consultant.user,
            )

    if instance.is_active:
        instance.add_permission(
            settings.RELATION_CANCEL_ROLE,
            instance.consultant.user,
        )
    else:
        instance.add_permission(
            settings.RELATION_ACTIVE_ROLE,
            instance.consultant.user,
        )

    projects_ecosystem_changed.send(
        sender=instance.consultant.user.__class__,
        user=instance.consultant.user)


def consultant_project_role_post_delete(sender, instance, *args, **kwargs):

    consultant = instance.consultant
    user = consultant.user

    keep_perms = consultant.roles.filter_by_project(instance.project).exists()

    if not keep_perms:
        signal_user_unassigned.send(
            sender=sender,
            project=instance.project,
            user=user,
        )

        instance.project.remove_permission(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            user,
        )

    if instance.has_manager_perms:
        signal_head_coach_removed.send(
            sender=sender,
            relation=instance,
        )


def add_exo_consultant_to_project_handler(sender, project, *args, **kwargs):
    exo_role = ExORole.objects.get(code=kwargs.get('exo_role_code'))
    consultant = kwargs.get('consultant')
    project.consultants_roles.get_or_create(consultant=consultant, exo_role=exo_role)
