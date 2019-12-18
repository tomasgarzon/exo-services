from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..manager.achievement import AchievementManager


class Achievement(TimeStampedModel):
    name = models.CharField(max_length=200)
    code = models.CharField(
        max_length=1,
        choices=settings.ACHIEVEMENT_CH_CODE,
    )
    rewards = models.ManyToManyField(
        'Reward', blank=True,
        related_name='achievements',
    )

    objects = AchievementManager()

    def __str__(self):
        return self.name

    def create_for_user(self, user):
        # create UserAchievement in Pending for user
        user_achievement = self.users.create(user=user)
        # create UserReward in Pending for user
        for reward in self.rewards.all():
            reward.users.create(
                user=user,
                extra_data=reward.extra_data,
            )
        return user_achievement

    def complete(self, user):
        self.users.get(user=user).complete()
