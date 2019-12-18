from guardian.models import UserObjectPermission

from django.conf import settings
from django.db.models import Subquery, IntegerField
from django.db.models.functions import Cast
from django.contrib.contenttypes.models import ContentType

from team.models import Team


def get_team_for_user(project, user):
    permissions_allowed_for_all_teams = [
        settings.PROJECT_CH_ROLE_LEVEL_ADMIN,
        settings.PROJECT_CH_ROLE_LEVEL_READONLY,
        settings.PROJECT_CH_ROLE_LEVEL_NOTIFICATIONS
    ]
    cond1 = user.is_superuser or project.created_by == user
    cond_permissions = False
    for permission in permissions_allowed_for_all_teams:
        user_has_perms = user.has_perm(permission, project)
        cond_permissions |= user_has_perms
    if cond1 or cond_permissions:
        return project.teams.all()

    query = project.teams.all().values_list('id', flat=True)

    teams_id = UserObjectPermission.objects.annotate(
        as_integer=Cast('object_pk', IntegerField())
    ).filter(
        user=user,
        content_type=ContentType.objects.get_for_model(Team),
        as_integer__in=Subquery(query)).values_list(
        'as_integer', flat=True)
    return Team.objects.filter(id__in=teams_id)
