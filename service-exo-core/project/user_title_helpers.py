from django.conf import settings

from exo_role.models import ExORole


def is_role_manager(exo_role):
    return exo_role.code in [
        settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
        settings.EXO_ROLE_CODE_FASTRACK_CURATOR,
        settings.EXO_ROLE_CODE_FASTRACK_CO_CURATOR,
    ]


def get_user_title_in_project(project, user):
    consultant_project_role = project.consultants_roles.filter(consultant__user=user)
    user_project_role = project.users_roles.filter(user=user)

    if not consultant_project_role.exists() and not user_project_role:
        return ''

    user_manager = [
        user_role for user_role in consultant_project_role if is_role_manager(user_role.exo_role)
    ]

    if user_manager:
        return user_manager[0].exo_role.name

    teams_coach = project.teams.filter(coach__user=user)
    if teams_coach.exists():
        return '{} {}'.format(
            '/'.join(list(teams_coach.values_list('name', flat=True))),
            ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH).name
        )

    user_project_role = user_project_role.first()

    if not user_project_role:
        return ''

    if user_project_role.is_delivery_manager:
        return user_project_role.exo_role.name

    teams_user = project.teams.filter(team_members=user)
    if user_project_role.is_member and teams_user:
        return '{} {}'.format(
            '/'.join(list(teams_user.values_list('name', flat=True))),
            ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).name
        )
    return ''
