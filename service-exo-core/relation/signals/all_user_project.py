from django.conf import settings
from ..category_helpers import (
    update_roles_by_category,
    update_role_for_project_role)


def all_user_project_when_added(sender, project, user, *args, **kwargs):
    # Perms for full access to project
    project.add_permission(
        settings.PROJECT_PERMS_VIEW_PROJECT,
        user,
    )


def all_user_project_when_removed(sender, project, user, *args, **kwargs):

    # Perms for full access to project
    project.remove_permission(
        settings.PROJECT_PERMS_VIEW_PROJECT,
        user,
    )


def update_visible_roles(sender, instance, *args, **kwargs):
    consultant_queryset = instance.consultants_roles.all()
    update_roles_by_category(instance, consultant_queryset)
    users_queryset = instance.users_roles.all()
    update_roles_by_category(instance, users_queryset)


def update_visible_project_role(sender, instance, *args, **kwargs):
    if instance.id is None:
        update_role_for_project_role(instance)
