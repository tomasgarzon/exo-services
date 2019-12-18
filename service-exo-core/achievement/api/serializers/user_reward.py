from rest_framework import serializers

from ...models import UserReward


class UserRewardSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='reward.code')

    class Meta:
        model = UserReward
        fields = ['extra_data', 'status', 'code']
