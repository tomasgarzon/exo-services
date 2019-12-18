from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from ..managers.assignment_step import AssignmentStepManager


class AssignmentStep(CreatedByMixin, TimeStampedModel):
    step = models.ForeignKey(
        'project.Step',
        related_name='assignments_step',
        on_delete=models.CASCADE)
    blocks = GenericRelation(
        'InformationBlock',
        related_query_name='assignments_step')
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    settings = JSONField(blank=True, null=True)
    streams = models.ManyToManyField(
        'utils.Stream',
        related_name='assignment_steps',
    )

    objects = AssignmentStepManager()

    class Meta:
        ordering = ['step__index', 'order']

    def __str__(self):
        return self.name

    @property
    def project(self):
        return self.step.project

    def _create_team_assignment_step(self, user_from, team):
        team_assignment_step, _ = self.assignment_step_teams.get_or_create(
            team=team,
            defaults={
                'created_by': user_from,
            }
        )
