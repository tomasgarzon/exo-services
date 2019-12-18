import tagulous

from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from .manager import KeywordManager
from .conf import settings  # noqa


class Keyword(CreatedByMixin, TimeStampedModel):
    name = models.CharField(max_length=200)
    public = models.BooleanField(
        blank=True, null=False,
        default=False,
    )
    tags = tagulous.models.TagField(
        force_lowercase=True,
        tree=True,
    )

    objects = KeywordManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
