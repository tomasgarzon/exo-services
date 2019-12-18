from django.db import models
from django.utils import timezone

from exo_role.models import ExORole

from project.models import Project

from ..managers import SprintManager
from ..conf import settings


class Sprint(Project):

    goals = models.TextField(
        verbose_name='Goals',
        null=True, blank=True,
    )

    challenges = models.TextField(
        verbose_name='Challenges',
        null=True, blank=True,
    )

    objects = SprintManager()

    class Meta:
        verbose_name_plural = 'ExO Sprints'
        verbose_name = 'ExO Sprint'
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)

    def update(
        self, user_from, name, customer, start, consultants=None,
        customer_members=None, **kwargs
    ):
        """
        Extends from ProjectMixin update to save Goals and Challenges
        """
        # Use project_ptr to avoid guardian permission issues
        self.project_ptr.update(
            user_from=user_from,
            name=name,
            customer=customer,
            customer_members=customer_members,
            start=start,
            consultants=consultants,
        )

        self.goals = kwargs.get('goals')
        self.challenges = kwargs.get('challenges')

        self.save(update_fields=['goals', 'challenges'])

        return self

    def get_week_description(self, date=None):
        if not date:
            date = timezone.now()
        week = self.current_week(date)
        if week:
            return settings.SPRINT_WEEK_DESCRIPTION[week - 1]
        return None

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
            'lapse': settings.PROJECT_LAPSE_WEEK,
            'steps': settings.SPRINT_DURATION_WEEK,
            'data': {'name': 'Step %s'},
            'populate': True,
        }

    @classmethod
    def get_roles_can_access_forum(cls):
        return {
            'consultant': [
                settings.EXO_ROLE_CODE_ADVISOR,
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
                settings.EXO_ROLE_CODE_SPRINT_COACH,
                settings.EXO_ROLE_CODE_ALIGN_TRAINER,
                settings.EXO_ROLE_CODE_SPRINT_REPORTER,
            ],
            'user': [
                settings.EXO_ROLE_CODE_SPRINT_OBSERVER,
                settings.EXO_ROLE_CODE_SPRINT_OTHER,
                settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
            ]
        }
