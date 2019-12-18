from django.conf import settings

from invitation.models import Invitation
from ecosystem.signals_define import projects_ecosystem_changed

from ..signals_define import signal_user_assigned, signal_user_unassigned


def user_project_role_post_save(sender, instance, created, *args, **kwargs):
    update_fields = kwargs.get('update_fields') or []

    if (created or 'status' in update_fields) and (instance.is_active):
        signal_user_assigned.send(
            sender=sender,
            project=instance.project,
            user=instance.user,
        )
        instance.project.resfresh_manager_permissions_for_user(instance.user)

        if instance.is_supervisor:
            instance.project.add_permission(
                settings.PROJECT_PERMS_ONLY_VIEW_PROJECT,
                instance.user,
            )

        if instance.is_delivery_manager:
            instance.project.add_permission(
                settings.PROJECT_PERMS_DELIVERY_MANAGER,
                instance.user,
            )
            instance.project.add_manager_permissions(instance.user)

    if instance.is_active:
        instance.add_permission(
            settings.RELATION_CANCEL_ROLE,
            instance.user,
        )
    else:
        instance.add_permission(
            settings.RELATION_ACTIVE_ROLE,
            instance.user,
        )
    projects_ecosystem_changed.send(
        sender=instance.user.__class__,
        user=instance.user)


def user_project_role_post_delete(sender, instance, *args, **kwargs):
    invitations = Invitation.objects.filter_by_object(instance)
    invitations.delete()
    has_other_user_relation = instance.user.projects_member.filter(project=instance.project).exists()
    has_other_consultant_relation = instance.user.is_consultant and instance.user.consultant.roles.filter_by_project(
        instance.project).exists()
    keep_perms = has_other_user_relation or has_other_consultant_relation

    if not keep_perms:
        signal_user_unassigned.send(
            sender=sender,
            project=instance.project,
            user=instance.user,
        )
        instance.project.resfresh_manager_permissions_for_user(
            new_user=instance.user,
            added=False,
        )

    if instance.is_supervisor:
        instance.project.remove_permission(
            settings.PROJECT_PERMS_ONLY_VIEW_PROJECT,
            instance.user,
        )

    if instance.is_delivery_manager:
        instance.project.remove_permission(
            settings.PROJECT_PERMS_DELIVERY_MANAGER,
            instance.user,
        )
