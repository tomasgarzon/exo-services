from django.db import models

from utils.dates import generate_dates

from ..queryset.step import StepQuerySet


class StepManager(models.Manager):
    use_for_related_fields = True
    queryset_class = StepQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_index_range(self, start, end):
        return self.get_queryset().filter_by_index_range(start, end)

    def start_steps(self, project):
        dates = generate_dates(
            start_date=project.start,
            timezone=project.timezone,
            lapses=list(project.steps.values_list('duration', flat=True))
        )

        for index, step in enumerate(project.steps.all()):
            start, end = dates[index]
            step.start = start
            step.end = end
            step.save()

    def modify_steps(self, project, from_step):
        steps = project.steps.filter(index__gte=from_step.index)
        dates = generate_dates(
            start_date=from_step.start,
            timezone=project.timezone,
            lapses=list(steps.values_list('duration', flat=True)))
        for index, step in enumerate(steps):
            start, end = dates[index]
            step.start = start
            step.end = end
            step.save()
