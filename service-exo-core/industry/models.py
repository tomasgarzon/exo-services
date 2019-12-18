from django.db import models
from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from .manager import IndustryManager


class Industry(CreatedByMixin, TimeStampedModel):
    name = models.CharField(max_length=100)
    public = models.BooleanField(
        blank=True, null=False,
        default=True,
    )

    objects = IndustryManager()

    class Meta:
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
        ordering = ['name']

    def __str__(self):
        return self.name
