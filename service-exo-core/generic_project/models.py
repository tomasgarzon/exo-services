from django.conf import settings
from django.db import models

from exo_role.models import ExORole

from project.models import Project
from validation.validators.generic_project import GenericProjectValidator


class GenericProject(Project):

    class Meta:
        verbose_name_plural = 'ExO Generic Projects'
        verbose_name = 'ExO Generic Project'
        ordering = ['name']

    description = models.TextField(
        verbose_name='Description',
        blank=True,
        null=True,
    )

    @staticmethod
    def validator_class():
        return GenericProjectValidator

    def get_roles(self):
        return {
            'manager': [
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
            ],
            'team_manager': [
                settings.EXO_ROLE_CODE_SPRINT_COACH,
                settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER,
            ],
            'consultant': list(ExORole.objects.filter(
                categories__code__in=[
                    settings.EXO_ROLE_CATEGORY_EXO_SPRINT,
                    settings.EXO_ROLE_CATEGORY_FASTRACK,
                    settings.EXO_ROLE_CATEGORY_CERTIFICATION_PROGRAM,
                ]
            ).values_list('code', flat=True)),
            'labels': ExORole.objects.filter(
                categories__code__in=[
                    settings.EXO_ROLE_CATEGORY_EXO_SPRINT,
                    settings.EXO_ROLE_CATEGORY_FASTRACK,
                    settings.EXO_ROLE_CATEGORY_CERTIFICATION_PROGRAM,
                ]
            ).values_list('code', 'name'),
            'multiplicity': [
                (settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH, '1'),
            ],
        }

    @classmethod
    def get_steps(cls, **kwargs):
        return {
            'lapse': settings.PROJECT_LAPSE_NO_APPLY,
            'steps': 0,
            'data': {'name': 'Period %s'},
            'populate': True,
        }
