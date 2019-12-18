from rest_framework import serializers

from ...tasks import EventUpdatedOwnerNotificationTask
from ...models import Event
from ...helpers import EventPermissionHelper
from .mixins import EventMixinSerializer


class EventStatusSerializer(EventMixinSerializer, serializers.ModelSerializer):

    comments = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Event
        fields = ['_status', 'comments']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context.get('view').request.user
        permission_helper = EventPermissionHelper()
        try:
            assert permission_helper.can_publish_event(user)
        except AssertionError:
            raise serializers.ValidationError('You can not perform this action')

        return attrs

    def update(self, instance, validated_data):
        instance.status = (self.context.get('view').request.user, validated_data.get('_status'))
        EventUpdatedOwnerNotificationTask().s(
            pk=instance.pk,
            comment=validated_data.get('comments', ''),
        ).apply_async()

        return instance
