from rest_framework import serializers

from ...models import Conversation
from .conversation_user import ConversationUserSerializer


class ConversationSerializer(serializers.ModelSerializer):

    total_unread = serializers.SerializerMethodField()
    users = ConversationUserSerializer(many=True)
    createdByUuid = serializers.UUIDField(source='created_by.uuid')
    UUIDRelatedObject = serializers.UUIDField(source='uuid_related_object')

    class Meta:
        model = Conversation
        read_only_fields = ['id', 'uuid']
        fields = [
            'id', 'name',
            'icon',
            'last_message_timestamp',
            'total_unread',
            'users',
            'createdByUuid',
            'UUIDRelatedObject',
            'uuid'
        ]

    def get_total_unread(self, obj):
        return obj.total_unread(self.context.get('request').user)
