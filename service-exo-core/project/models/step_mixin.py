from django.db import models
from django.conf import settings
from django.utils import timezone


class StepMixin(models.Model):

    lapse = models.CharField(
        choices=settings.PROJECT_CH_LAPSE,
        max_length=1,
        blank=True, null=True,
    )

    class Meta:
        abstract = True

    @property
    def lapse_type(self):
        return self.lapse

    @property
    def first_day(self):
        """
        Service start date AWARED
        """
        if not self.steps.exists():
            return self.start
        return self.steps.first().start

    @property
    def last_day(self):
        """
        Service end date AWARED
        """
        if not self.steps.exists():
            return self.end
        return self.steps.last().end

    def current_week(self, date=None):
        if not date:
            date = timezone.now()
        steps = self.steps.filter(start__lte=date, end__gte=date)
        if steps:
            return steps[0].index
        return 0

    def current_step(self, date=None):
        if not date:
            date = timezone.now()
        steps = self.steps.filter(start__lte=date, end__gte=date)
        if steps:
            return steps.first()
        steps = self.steps.filter(start__lte=date).order_by('-start')
        if steps:
            return steps.first()
        steps = self.steps.filter(end__lte=date).order_by('-end')
        if steps:
            return steps.first()

        return self.steps.first()

    def get_project_start_date(self):
        start_step = self.steps.filter(start__isnull=False).first()
        start_date = None
        if self.start:
            start_date = self.start
        elif start_step:
            start_date = start_step.start
        return start_date

    def get_project_end_date(self):
        end_step = self.steps.filter(end__isnull=False).last()
        end_date = None
        if self.end:
            end_date = self.end
        elif end_step:
            end_date = end_step.end
        return end_date
