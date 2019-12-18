from rest_framework import serializers

from consultant.api.serializers.requirement import RequirementSerializer

from ...models import UserAchievement
from .user_reward import UserRewardSerializer


class UserAchievementSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='achievement.code')
    user = serializers.IntegerField(source='user_id')
    rewards = UserRewardSerializer(
        many=True,
    )
    requirements = RequirementSerializer(source='user')

    class Meta:
        model = UserAchievement
        fields = ['pk', 'code', 'status', 'user', 'rewards', 'requirements']
