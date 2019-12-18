from guardian.shortcuts import get_objects_for_user

from django.conf import settings


def get_team_for_user(project, user):
    permissions_allowed_for_all_teams = [
        settings.PROJECT_PERMS_PROJECT_MANAGER,
        settings.PROJECT_PERMS_ONLY_VIEW_PROJECT,
        settings.PROJECT_PERMS_DELIVERY_MANAGER
    ]
    cond1 = user.is_superuser
    cond_permissions = False
    for permission in permissions_allowed_for_all_teams:
        user_has_perms = user.has_perm(permission, project)
        cond_permissions |= user_has_perms
    if cond1 or cond_permissions:
        return project.teams.all()
    teams = get_objects_for_user(user, settings.TEAM_FULL_VIEW)
    return teams.filter_by_project(project)
