from django.db import models

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ..conf import settings


class UserAchievement(ChoicesDescriptorMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='achievements',
        on_delete=models.CASCADE,
    )
    achievement = models.ForeignKey(
        'Achievement',
        related_name='users',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=1,
        default=settings.ACHIEVEMENT_STATUS_DEFAULT,
        choices=settings.ACHIEVEMENT_STATUS_CH_STATUS,
        blank=False, null=False,
    )

    def __str__(self):
        return '{} - {} - Status: {}'.format(
            self.user,
            self.achievement,
            self.get_status_display(),
        )

    def set_status(self, new_status):
        self.status = new_status
        self.save(update_fields=['status', 'modified'])

    def complete(self):
        self.set_status(settings.ACHIEVEMENT_STATUS_CH_COMPLETED)
        self.complete_reward()
        self.update_realtime()

    def complete_reward(self):
        for user_reward in self.rewards:
            user_reward.complete()

    @property
    def rewards(self):
        return self.user.rewards.filter(reward__achievements=self.achievement)

    def update_realtime(self):
        pass
