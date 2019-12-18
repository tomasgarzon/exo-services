from django.db import models

from ..conf import settings


class StepStreamQuerySet(models.QuerySet):

    FILTER_DESCRIPTORS = [{
        'field': 'stream',
        'options': settings.PROJECT_STREAM_CH_TYPE,
    }]

    def filter_by_step(self, step):
        return self.filter(step=step)

    def filter_by_stream(self, stream):
        return self.filter(stream=stream)
