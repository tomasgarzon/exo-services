from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin

from ..managers.assignment_task_team import AssignmentTaskTeamManager


class AssignmentTaskTeam(CreatedByMixin, TimeStampedModel):
    assignment_step_team = models.ForeignKey(
        'AssignmentStepTeam', related_name='assignment_tasks_team',
        on_delete=models.CASCADE)
    assignment_task_item = models.ForeignKey(
        'AssignmentTaskItem', related_name='assignment_tasks_team',
        on_delete=models.CASCADE)
    status = models.CharField(
        max_length=1,
        choices=settings.ASSIGNMENT_TASK_TEAM_CH_STATUS,
        default=settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DEFAULT,
    )

    objects = AssignmentTaskTeamManager()

    class Meta:
        unique_together = ('assignment_step_team', 'assignment_task_item')

    def __str__(self):
        return self.assignment_task_item.name

    @property
    def team(self):
        return self.assignment_step_team.team
