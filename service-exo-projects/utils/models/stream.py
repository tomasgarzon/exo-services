from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class Stream(TimeStampedModel):
    name = models.CharField(
        max_length=255)
    code = models.CharField(
        max_length=1,
        choices=settings.UTILS_STREAM_CH_TYPE)
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        related_name='streams')

    def __str__(self):
        return self.name
