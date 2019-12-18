from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings  # noqa


class Language(TimeStampedModel):

    name = models.CharField(verbose_name='Language Name', max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
