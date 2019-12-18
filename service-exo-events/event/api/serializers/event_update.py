from django.conf import settings
from django.db.models.signals import pre_delete
from rest_framework import serializers

from ...models import Event


class EventChangeStatusSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        source='_status',
        choices=settings.EVENT_STATUS_CHOICES,
    )

    class Meta:
        model = Event
        fields = ['status', ]

    def update(self, instance, validated_data):
        user_from = validated_data.get('user_from')
        if validated_data.get('_status') == settings.EVENT_CH_STATUS_DELETED:
            pre_delete.send(
                sender=instance.__class__,
                instance=instance)
        instance.status = (user_from, validated_data.get('_status'))

        return instance
