from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from ..managers.step import StepManager
from .mixins import StepFeedbackMixin


class Step(StepFeedbackMixin, TimeStampedModel):
    project = models.ForeignKey(
        'Project',
        related_name='steps',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    index = models.IntegerField(blank=False, null=False)
    duration = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        blank=True, null=True,
        choices=settings.PROJECT_CH_STATUS_STEP,
        default=settings.PROJECT_CH_STATUS_STEP_FUTURE)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)

    objects = StepManager()

    class Meta:
        ordering = ['project', 'index']

    def __str__(self):
        return '{}-{}'.format(self.project.name, self.name)

    @property
    def user_has_to_fill_feedback(self):
        return self.index != 1

    @property
    def current(self):
        return self.project.current_step() == self

    def has_team_assignments(self, team):
        return self.assignments_step.filter_by_stream(team.stream).exists()

    def set_current(self):
        self.status = settings.PROJECT_CH_STATUS_STEP_CURRENT
        self.save()

    def set_past(self):
        self.status = settings.PROJECT_CH_STATUS_STEP_PAST
        self.save()

    def set_future(self):
        self.status = settings.PROJECT_CH_STATUS_STEP_FUTURE
        self.save()
