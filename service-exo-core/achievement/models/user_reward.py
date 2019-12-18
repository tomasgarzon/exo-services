from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ..conf import settings


class UserReward(ChoicesDescriptorMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rewards',
        on_delete=models.CASCADE,
    )
    reward = models.ForeignKey(
        'Reward',
        related_name='users',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=1,
        default=settings.ACHIEVEMENT_STATUS_DEFAULT,
        choices=settings.ACHIEVEMENT_STATUS_CH_STATUS,
        blank=False, null=False,
    )
    extra_data = JSONField()

    def __str__(self):
        return '{} - {} - Status: {}'.format(
            self.user,
            self.reward,
            self.get_status_display(),
        )

    def set_status(self, new_status):
        self.status = new_status
        self.save(update_fields=['status', 'modified'])

    def complete(self):
        self.set_status(settings.ACHIEVEMENT_STATUS_CH_COMPLETED)
