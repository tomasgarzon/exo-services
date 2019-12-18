from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


# Create your models here.
class TrainingSession(CreatedByMixin, TimeStampedModel):
    name = models.CharField(max_length=150)
    description = models.CharField(
        max_length=200,
        blank=True, null=True,
    )
    date = models.DateField(
        blank=True, null=True,
    )

    def __str__(self):
        return self.name
