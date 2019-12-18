from django.db import models
from model_utils.models import TimeStampedModel


class Industry(TimeStampedModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ['name']

    def __str__(self):
        return self.name
