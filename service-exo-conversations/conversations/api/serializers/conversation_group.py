from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.conf import settings

from files.api.serializers.uploaded_file import UploadedFileSerializer
from files.models import UploadedFile

from ...models import Conversation


class UserSerializer(serializers.Serializer):
    user_uuid = serializers.UUIDField()
    name = serializers.CharField()
    profile_picture = serializers.CharField()
    short_title = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    profile_url = serializers.CharField()


class GroupNameSerializer(serializers.Serializer):
    name = serializers.CharField()
    icon = serializers.CharField(required=False, allow_null=True)
    users = UserSerializer(many=True)


class CreateGroupConversationSerializer(serializers.Serializer):
    user_from = serializers.CharField(required=True)
    groups = GroupNameSerializer(many=True)
    group_type = serializers.ChoiceField(
        choices=settings.CONVERSATIONS_CH_OPTIONS)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    files = UploadedFileSerializer(many=True, required=False)

    def prepare_user_for_conversation(self, group):
        users = []
        for user in group.get('users'):
            user_data = user.copy()
            user_uuid = user_data.pop('user_uuid')
            user, _ = get_user_model().objects.get_or_create(uuid=user_uuid)
            user_data['user'] = user
            users.append(user_data)
        return users

    def create(self, validated_data):
        user_from = validated_data.get('user_from')
        conversations = []
        for group in validated_data.get('groups'):
            users = self.prepare_user_for_conversation(group)
            conversation = Conversation.objects.initialize_conversation(
                name=group.get('name'),
                conversation_type=validated_data.get('group_type'),
                related_uuid=validated_data.get('related_to'),
                user_from=user_from,
                users=users,
                icon=group.get('icon'),
            )
            conversations.append(conversation)

        if validated_data.get('message') or validated_data.get('files'):
            conversation = conversations[0]
            message = conversation.add_message(
                user_from, validated_data.get('message'))
            for data in validated_data.get('files', []):
                UploadedFile.create(
                    created_by=validated_data.get('user_from'),
                    filename=data.get('filename'),
                    mimetype=data.get('mimetype'),
                    filestack_url=data.get('url'),
                    filestack_status=data.get('filestack_status'),
                    related_to=message)
        return conversations


class UpdateGroupConversationSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    icon = serializers.CharField(required=False, allow_null=True)
    users = UserSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ['name', 'icon', 'users']

    def update(self, conversation, validated_data):
        Conversation.objects.update_conversation(
            conversation,
            **validated_data)
        return conversation
