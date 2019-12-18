from django.conf import settings

from exo_role.models import ExORole

from project.models import Project
from validation.validators.project import FastrackValidator

from .manager import FastrackSprintManager
from .conf import settings as settings_app  # noqa


class FastrackSprint(Project):

    objects = FastrackSprintManager()

    class Meta:
        verbose_name_plural = 'Fastracks'
        verbose_name = 'Fastrack'
        ordering = ['name']

    @classmethod
    def validator_class(cls):
        return FastrackValidator

    def get_roles(self):
        return {
            'manager': [
                settings.EXO_ROLE_CODE_FASTRACK_CURATOR,
                settings.EXO_ROLE_CODE_FASTRACK_CO_CURATOR,
            ],
            'team_manager': [
                settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER,
            ],
            'consultant': list(ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_FASTRACK).values_list('code', flat=True)),
            'labels': ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_FASTRACK).values_list('code', 'name'),
            'multiplicity': [],
        }

    @classmethod
    def get_steps(cls, **kwargs):
        if kwargs.get('version_2'):
            return {
                'steps': settings.FASTRACK_STEPS_COUNT,
                'template': 'fastrack',
                'populate': True,
            }
        else:
            return cls.get_steps_v1()

    @classmethod
    def get_steps_v1(cls):
        return {
            'steps': 0,
            'lapse': settings.PROJECT_LAPSE_NO_APPLY,
            'populate': False,
        }
