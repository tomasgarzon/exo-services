from rest_framework import serializers

from ...models import UserSubscription


class UserSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSubscription
        fields = ['user_uuid', 'subscription']


class SubscribeSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    subscription = serializers.CharField()

    def create(self, validated_data):
        user_uuid = validated_data.pop('uuid')
        subscription = validated_data.pop('subscription')
        user_subscription, _ = UserSubscription.objects.get_or_create(
            user_uuid=user_uuid,
            subscription=subscription)
        return validated_data

    def to_representation(self, *args, **kwargs):
        return {}


class UnsubscribeSerializer(serializers.Serializer):
    uuid = serializers.UUIDField()
    subscription = serializers.CharField()

    def create(self, validated_data):
        user_uuid = validated_data.pop('uuid')
        subscription = validated_data.pop('subscription')
        UserSubscription.objects.filter(
            user_uuid=user_uuid,
            subscription=subscription).delete()
        return validated_data

    def to_representation(self, *args, **kwargs):
        return {}
