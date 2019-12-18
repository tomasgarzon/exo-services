from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class Badge(TimeStampedModel):
    code = models.CharField(
        max_length=5,
        choices=settings.BADGE_CODE_CHOICES,
        blank=True, null=True,
    )
    category = models.CharField(
        max_length=2,
        choices=settings.BADGE_CATEGORY_CHOICES,
    )
    order = models.IntegerField(default=1)

    def __str__(self):
        return '{} - {}'.format(self.get_category_display(), self.get_code_display())
