from rest_framework import serializers

from django.contrib.auth import get_user_model

from files.api.serializers.uploaded_file import UploadedFileSerializer
from files.api.serializers.uploaded_file_reverse import UploadedFileRelatedGenericSerializer
from files.models import UploadedFile

from ...models import Message


class MessageSerializer(serializers.ModelSerializer):

    unread = serializers.SerializerMethodField()
    user = serializers.UUIDField(source='created_by.uuid')
    files = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'created',
            'modified',
            'unread',
            'user',
            'message',
            'files',
        ]

    def get_unread(self, obj):
        return not obj.seen(self.context.get('request').user)

    def get_files(self, obj):
        return UploadedFileRelatedGenericSerializer(
            obj.files.all(), many=True, context=self.context).data


class CreateMessageSerializer(serializers.ModelSerializer):
    files = UploadedFileSerializer(many=True, required=False)

    class Meta:
        model = Message
        fields = ['message', 'files']

    def create(self, validated_data):
        conversation = validated_data.get('conversation')
        message = conversation.add_message(
            user_from=validated_data.get('user_from'),
            message=validated_data.get('message'))
        for data in validated_data.get('files', []):
            UploadedFile.create(
                created_by=validated_data.get('user_from'),
                filename=data.get('filename'),
                mimetype=data.get('mimetype'),
                filestack_url=data.get('url'),
                filestack_status=data.get('filestack_status'),
                related_to=message)
        return message


class CreateMessageFromServiceSerializer(serializers.Serializer):
    conversation_created_by = serializers.UUIDField()
    created_by = serializers.UUIDField()
    message = serializers.CharField()

    def create(self, validated_data):
        conversation = validated_data.get('conversation')
        user_from = get_user_model().objects.get(
            uuid=validated_data.get('created_by'))
        return conversation.add_message(
            user_from=user_from,
            message=validated_data.get('message'))
