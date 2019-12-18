from project.models import Project
from exo_role.models import ExORole

from validation.validators import WorkshopValidator

from ..managers.workshop import WorkshopManager
from ..conf import settings


class WorkShop(Project):

    objects = WorkshopManager()

    class Meta:
        verbose_name_plural = 'ExO Certification Workshops'
        verbose_name = 'ExO Certification Workshop'

    def get_roles(self):
        return {
            'manager': [
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
                settings.EXO_ROLE_CODE_WORKSHOP_TRAINER,
            ],
            'team_manager': [
                settings.EXO_ROLE_CODE_SPRINT_COACH,
            ],
            'consultant': list(ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_WORKSHOP).values_list('code', flat=True)),
            'labels': ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_WORKSHOP).values_list('code', 'name'),
            'multiplicity': [
                (settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH, 'n'),
            ],
        }

    @classmethod
    def get_steps(cls, **kwargs):
        return {
            'lapse': settings.PROJECT_LAPSE_DAY,
            'steps': settings.WORKSHOP_DURATION_DAYS,
            'data': {'name': 'Step %s'},
            'populate': True,
        }

    @classmethod
    def get_roles_can_access_forum(cls):
        return {
            'consultant': [
                settings.EXO_ROLE_CODE_ADVISOR,
                settings.EXO_ROLE_CODE_WORKSHOP_TRAINER,
                settings.EXO_ROLE_CODE_SPRINT_COACH,
            ],
            'user': [
                settings.EXO_ROLE_CODE_SPRINT_OBSERVER,
                settings.EXO_ROLE_CODE_SPRINT_OTHER,
                settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
            ]
        }

    @staticmethod
    def validator_class():
        return WorkshopValidator
