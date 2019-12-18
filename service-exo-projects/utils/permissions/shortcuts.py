from django.conf import settings


def has_project_perms(project, perms, user, related=None, for_write=True):
    """
        Check permission in project
        - project: project
        - perms: permission name
        - user: user
        - related: related object, can be null
        - for_write: by default, True. If you want to check for read only, pass False
    """
    # Check perms View Project (project member)
    if not user.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT, project):
        return False

    cond1 = user.is_superuser
    cond2 = user.has_perm(settings.PROJECT_PERMS_PROJECT_MANAGER, project)
    cond3 = False if for_write else user.has_perm(settings.PROJECT_PERMS_ONLY_VIEW_PROJECT, project)
    if cond1 or cond2 or cond3:
        return True
    if related:
        return user.has_perm(perms, related)
    else:
        return user.has_perm(perms, project)


def has_team_perms(team, perms, user, related=None, for_write=True):
    """
        Check permission in team
        - team: team
        - perms: permission name
        - user: user
        - related: related object, can be null
        - for_write: by default, True. If you want to check for read only, pass False
    """
    # Check perms View Project (project member)
    if not user.has_perm(
        settings.PROJECT_PERMS_VIEW_PROJECT,
        team.project,
    ):
        return False

    cond1 = user.is_superuser
    cond2 = user.has_perm(
        settings.PROJECT_PERMS_PROJECT_MANAGER,
        team.project,
    )
    cond3 = False if for_write else user.has_perm(settings.PROJECT_PERMS_ONLY_VIEW_PROJECT, team.project)
    if cond1 or cond2 or cond3:
        return True

    # Check perms View Team (team member)
    if not user.has_perm(settings.TEAM_PERMS_FULL_VIEW_TEAM, team):
        return False

    cond3 = user.has_perm(settings.TEAM_PERMS_COACH_TEAM, team)
    if cond3:
        return True
    if related:
        return user.has_perm(perms, related)
    else:
        return user.has_perm(perms, team)
