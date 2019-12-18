from django.db import models

from django_extensions.db.fields import AutoSlugField
from model_utils.models import TimeStampedModel

from ..managers.tag import TagManager


class Tag(TimeStampedModel):
    name = models.CharField(
        blank=False, null=False,
        max_length=255, unique=True)
    slug = AutoSlugField(
        populate_from='name',
        null=False,
        blank=False,
        unique=True)
    category = models.ForeignKey(
        'resource.Category',
        blank=True, null=True,
        related_name='tags',
        on_delete=models.deletion.SET_NULL)
    default_show_filter = models.BooleanField(default=False)
    extra_data = models.TextField(blank=True, null=True)
    objects = TagManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
