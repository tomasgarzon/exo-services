from django.db import models
from model_utils.models import TimeStampedModel

from .conf import settings


class ExOAttribute(TimeStampedModel):
    name = models.CharField(max_length=100)
    _type = models.CharField(
        max_length=1,
        choices=settings.EXO_ATTRIBUTES_CH_EXO_TYPE,
    )
    order = models.IntegerField()

    class Meta:
        verbose_name = 'ExOAttribute'
        verbose_name_plural = 'ExOAttributes'
        ordering = ['order']

    def __str__(self):
        return self.name
