from django.db import models

from exo_role.models import ExORole

from project.models import Project
from validation.validators.sprint_automated import SprintAutomatedValidator

from ..managers.sprint_automated import SprintAutomatedManager
from ..conf import settings


class SprintAutomated(Project):

    description = models.TextField(
        verbose_name='description',
        null=True, blank=True
    )

    accomplish = models.CharField(
        max_length=1,
        choices=settings.SPRINT_AUTOMATED_CH_ACCOMPLISH,
        default=settings.SPRINT_AUTOMATED_CH_ACCOMPLISH_1,
    )

    transform = models.CharField(
        max_length=1,
        choices=settings.SPRINT_AUTOMATED_CH_TRANSFORM,
        default=settings.SPRINT_AUTOMATED_CH_TRANSFORM_1,
    )

    playground = models.CharField(
        max_length=1,
        choices=settings.SPRINT_AUTOMATED_CH_PLAYGROUND,
        default=settings.SPRINT_AUTOMATED_CH_PLAYGROUND_1,
    )

    objects = SprintAutomatedManager()

    class Meta:
        verbose_name_plural = 'ExO Automated Sprints'
        verbose_name = 'ExO Automated Sprint'
        ordering = ['name']

    @staticmethod
    def validator_class():
        return SprintAutomatedValidator

    def get_roles(self):
        return {
            'manager': [
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
            ],
            'team_manager': [
                settings.EXO_ROLE_CODE_SPRINT_COACH,
            ],
            'consultant': list(ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_EXO_SPRINT).values_list('code', flat=True)),
            'labels': ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_EXO_SPRINT).values_list('code', 'name'),
            'multiplicity': [
                (settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH, '1'),
            ],
        }

    @classmethod
    def get_steps(cls, **kwargs):
        return {
            'template': 'sprint_book',
            'populate': True,
        }

    def update_first_step_dates(self):
        if self.steps.all().exists():
            first_step = self.steps.all()[0]
            second_step = self.steps.all()[1]
            first_step.start = self.start
            first_step.end = second_step.start
            first_step.save(update_fields=['start', 'end'])
