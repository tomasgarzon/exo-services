from django.db import models

from utils.descriptors import CustomFilterDescriptorMixin

from ..queryset.step_stream import StepStreamQuerySet
from ..conf import settings


class StepStreamManager(CustomFilterDescriptorMixin, models.Manager):

    use_for_related_fields = True
    queryset_class = StepStreamQuerySet

    FILTER_DESCRIPTORS = [{
        'field': 'stream',
        'options': settings.PROJECT_STREAM_CH_TYPE,
    }]

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_step(self, step):
        return self.get_queryset().filter_by_step(step)

    def filter_by_stream(self, stream):
        return self.get_queryset().filter_by_stream(stream)
