from django.db import models
from model_utils.models import TimeStampedModel

from .conf import settings


class ExOArea(TimeStampedModel):

    order = models.IntegerField()

    name = models.CharField(max_length=100)
    code = models.CharField(
        max_length=150,
        choices=settings.EXO_AREA_CH_EXO_AREAS_CODE,
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'ExOArea'
        verbose_name_plural = 'ExOAreas'
        ordering = ['order']

    def __str__(self):
        return self.name
