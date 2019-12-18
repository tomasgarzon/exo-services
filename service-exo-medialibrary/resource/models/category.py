from django.db import models

from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel

from ..managers.category import CategoryManager


class Category(TimeStampedModel):
    name = models.CharField(
        blank=False, null=False,
        max_length=255, unique=True)
    slug = AutoSlugField(
        populate_from='name',
        null=False,
        blank=False,
        unique=True)
    extra_data = models.TextField(blank=True, null=True)
    objects = CategoryManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
