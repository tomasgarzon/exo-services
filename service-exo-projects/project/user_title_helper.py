from django.conf import settings


def get_user_title_in_project(project, user, team=None):
    COACH = settings.EXO_ROLE_CODE_SPRINT_COACH
    PARTICIPANT = settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT

    user_title = []

    if team is None:
        project_roles = user.user_project_roles.filter(
            project_role__project=project).values_list('project_role__exo_role__name', flat=True)
    else:
        project_roles = user.user_project_roles.filter(
            project_role__project=project).exclude(
            project_role__code__in=[COACH, PARTICIPANT]).values_list('project_role__exo_role__name', flat=True)

    user_title.extend(sorted(list(project_roles)))
    team_roles = user.user_team_roles.filter(
        team=team).values_list('team_role__role', flat=True)
    team_roles_name = [
        '{} {}'.format(team.name, role) for role in team_roles
    ]
    user_title.extend(sorted(team_roles_name))

    return ', '.join(user_title)
