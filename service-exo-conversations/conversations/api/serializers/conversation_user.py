from rest_framework import serializers

from ...models import ConversationUser


class ConversationUserSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField()
    user_title = serializers.CharField(source='short_title')
    slug = serializers.CharField()

    class Meta:
        model = ConversationUser
        fields = [
            'name', 'profile_picture', 'profile_url',
            'user_title', 'uuid', 'slug']
