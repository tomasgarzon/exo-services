from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from .assignment_step import AssignmentStep
from .assignment_step_team import AssignmentStepTeam
from .assignment_task_team import AssignmentTaskTeam
from ..conf import settings


class AssignmentTaskItem(CreatedByMixin, TimeStampedModel):
    assignment_task = models.ForeignKey(
        'AssignmentTask',
        related_name='assignment_task_items',
        on_delete=models.CASCADE)
    blocks = GenericRelation('InformationBlock', related_query_name='assignment_task_items')
    name = models.TextField(max_length=512)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def project(self):
        return self.assignment_task.block.content_object.step.project

    @property
    def step(self):
        return self.assignment_task.block.content_object.step

    def get_status(self, team):
        try:
            return AssignmentTaskTeam.objects.filter_by_task_item(
                self).filter_by_team(team)[0].status
        except IndexError:
            return settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_TO_DO

    def mark_as_done(self, user_from, step, team):
        self.mark_status(user_from, step, team, settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE)

    def mark_as_to_do(self, user_from, step, team):
        self.mark_status(user_from, step, team, settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_TO_DO)

    def mark_status(self, user_from, step, team, status):
        is_admin = team.user_is_admin(user_from) or team.project.user_is_admin(user_from)
        if not is_admin and not team.user_is_basic(user_from):
            raise ValidationError('{} has no permissions: '.format(user_from))

        assignment_step = AssignmentStep.objects.filter(step=step).filter_by_stream(team.stream).first()
        assignment_step_team = AssignmentStepTeam.objects.get(assignment_step=assignment_step, team=team)
        defaults = {
            'status': status,
            'created_by': user_from
        }
        assignment_task_team, _ = AssignmentTaskTeam.objects.update_or_create(
            assignment_step_team=assignment_step_team,
            assignment_task_item=self,
            defaults=defaults)
