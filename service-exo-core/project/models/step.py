from django.db import models

from model_utils.models import TimeStampedModel
from utils.dates import localize_date

from ..managers.step import StepManager
from ..conf import settings
from .mixins import StepFeedbackMixin


class Step(StepFeedbackMixin, TimeStampedModel):

    project = models.ForeignKey(
        'Project',
        related_name='steps',
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        verbose_name='Name',
        max_length=100,
    )

    index = models.IntegerField(blank=False, null=False)

    status = models.CharField(
        max_length=1,
        default=settings.PROJECT_STEP_STATUS_DEFAULT,
        choices=settings.PROJECT_CH_STEP_STATUS,
        blank=False, null=False,
    )

    start = models.DateTimeField(blank=True, null=True)
    end = models.DateTimeField(blank=True, null=True)

    objects = StepManager()

    class Meta:
        verbose_name_plural = 'Steps'
        verbose_name = 'Step'
        ordering = ['index']

    def __str__(self):
        return self.short_name

    @property
    def is_week(self):
        return self.project.lapse == settings.PROJECT_LAPSE_WEEK

    @property
    def is_day(self):
        return self.project.lapse == settings.PROJECT_LAPSE_DAY

    @property
    def is_period(self):
        return self.project.lapse == settings.PROJECT_LAPSE_PERIOD

    @property
    def lapse_type(self):
        return self.project.lapse

    @property
    def lapse_type_display(self):
        return self.project.get_lapse_display()

    @property
    def short_name(self):
        if self.project.is_version_2:
            short_name = self.name
        else:
            short_name = '{} {}'.format(self.lapse_type_display, self.index)

        return short_name

    @property
    def start_tz(self):
        return localize_date(self.start, time_zone=self.project.timezone) if self.start else None

    @property
    def end_tz(self):
        return localize_date(self.end, time_zone=self.project.timezone) if self.end else None

    def start_step(self, date):
        # TODO check date from others steps
        self.start = date[0]
        self.end = date[1]
        self.save(update_fields=['start', 'end'])

    def guidelines(self, stream):
        guidelines = []
        try:
            step_stream = self.streams.filter(stream=stream)[0]
            guidelines = step_stream.guidelines
        except IndexError:
            pass
        return guidelines

    @property
    def user_has_to_fill_feedback(self):
        return self.index != 1

    @property
    def current(self):
        return self.project.current_step() == self

    def has_team_assignments(self, team):
        if self.project.is_version_2:
            return self.assignments_step.filter_by_stream(team.stream).exists()
        else:
            return self.project.assignments.filter_by_stream(team.stream).exists()
