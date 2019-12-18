from django.db import models
from django.contrib.auth import get_user_model

from exo_role.models import ExORole

from ..models import Team
from ..conf import settings


class UserTeamRoleQuerySet(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(team__project=project)

    def filter_by_role(self, role):
        return self.filter(team_role__code=role)

    def filter_by_team(self, team):
        return self.filter(team=team)

    def filter_by_level(self, level):
        return self.filter(team_role__level__icontains=level)

    def filter_by_manager(self):
        return self.filter_by_level(settings.PROJECT_CH_ROLE_LEVEL_ADMIN)

    def actives_only(self):
        return self.filter(active=True)

    def users(self):
        users_roles_ids = self.values_list('user_id', flat=True)
        return get_user_model().objects.filter(id__in=list(users_roles_ids))

    def teams(self):
        teams_ids = self.values_list('team_id', flat=True)
        return Team.objects.filter(id__in=list(teams_ids))

    def exo_roles(self):
        roles_ids = self.values_list('team_role__code', flat=True)
        return ExORole.objects.filter(code__in=roles_ids)
