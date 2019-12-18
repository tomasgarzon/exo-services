from django.db import models

from ..queryset.step_stream import StepStreamQuerySet


class StepStreamManager(models.Manager):
    use_for_related_fields = True
    queryset_class = StepStreamQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_step(self, step):
        return self.get_queryset().filter_by_step(step)

    def filter_by_stream(self, stream):
        return self.get_queryset().filter_by_stream(stream)
