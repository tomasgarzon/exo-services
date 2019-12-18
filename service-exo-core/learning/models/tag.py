from django.db import models
from model_utils.models import TimeStampedModel


class Tag(TimeStampedModel):
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
