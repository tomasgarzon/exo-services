from django.db import models

from model_utils.models import TimeStampedModel
from .manager import LanguageManager


class Language(TimeStampedModel):

    name = models.CharField(
        verbose_name='Language Name', max_length=100)
    objects = LanguageManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
