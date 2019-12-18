from django.db import models
from django.contrib.auth import get_user_model

from exo_role.models import ExORole

from ..conf import settings
from ..models import ProjectRole


class UserProjectRoleQuerySet(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(project_role__project=project)

    def filter_by_role(self, role):
        return self.filter(project_role__code=role)

    def filter_by_level(self, level):
        return self.filter(project_role__level__icontains=level)

    def filter_by_manager(self):
        return self.filter_by_level(settings.PROJECT_CH_ROLE_LEVEL_ADMIN)

    def users(self):
        user_ids = self.values_list('user_id', flat=True)
        return get_user_model().objects.filter(id__in=user_ids)

    def actives_only(self):
        return self.filter(active=True)

    def roles(self):
        roles_ids = self.values_list('project_role_id', flat=True)
        return ProjectRole.objects.filter(id__in=roles_ids)

    def exo_roles(self):
        roles_ids = self.values_list('project_role__exo_role_id', flat=True)
        return ExORole.objects.filter(id__in=roles_ids)
