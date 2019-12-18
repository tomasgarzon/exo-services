from django.contrib.auth import get_user_model
from django.conf import settings

from consultant.models import Consultant
from project.models import Project
from utils.queryset import QuerySetFilterComplexMixin

from .role import ExORoleQuerySet


class ConsultantProjectQuerySet(QuerySetFilterComplexMixin, ExORoleQuerySet):

    _fields_from_form = {
        'search': [
            'consultant__user__short_name__icontains',
            'exo_role__name__icontains',
        ],
    }

    def filter_by_project(self, project):
        return self.filter(project=project)

    def filter_by_user(self, user):
        return self.filter(consultant__user=user)

    def filter_by_exo_role(self, exo_role):
        return self.filter(exo_role=exo_role)

    def filter_by_exo_role_code(self, code):
        return self.filter(exo_role__code=code)

    def consultants(self):
        consultant_ids = self.values_list('consultant_id', flat=True)
        return Consultant.objects.filter(id__in=consultant_ids)

    def projects(self):
        project_ids = self.values_list('project_id', flat=True)
        return Project.objects.filter(id__in=project_ids)

    def users(self):
        user_ids = self.values_list('consultant__user_id', flat=True)
        return get_user_model().objects.filter(id__in=user_ids)

    def exclude_draft_projects(self):
        return self.exclude(project__status=settings.PROJECT_CH_PROJECT_STATUS_DRAFT)
