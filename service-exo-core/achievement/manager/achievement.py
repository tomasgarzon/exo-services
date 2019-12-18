from django.db import models
from django.conf import settings


class AchievementManager(models.Manager):

    def create_reward_for_consultant(self, consultant, number_of_coins=None):
        if number_of_coins is None:
            return
        achievement = self.get_queryset().get(
            code=settings.ACHIEVEMENT_CH_CODE_FILL_PROFILE,
        )
        user_achievement = achievement.create_for_user(consultant.user)
        user_reward = achievement.rewards.first().users.filter(user=consultant.user).first()
        # TODO: fill link when we have information about coins integration
        user_reward.extra_data['link'] = ''
        user_reward.extra_data['coins'] = number_of_coins
        user_reward.save()
        return user_achievement
