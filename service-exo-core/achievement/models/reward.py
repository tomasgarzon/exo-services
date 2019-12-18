from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel
from ..conf import settings


class Reward(TimeStampedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(
        max_length=1,
        choices=settings.ACHIEVEMENT_REWARD_CH_CODE,
    )
    extra_data = JSONField()

    def __str__(self):
        return self.name
