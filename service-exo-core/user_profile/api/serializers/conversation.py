from rest_framework import serializers

from files.api.serializers.uploaded_file import UploadedFileSerializer

from ...conversation_helpers import start_conversation


class StartConversationSerializer(serializers.Serializer):
    files = UploadedFileSerializer(many=True, required=False)
    message = serializers.CharField()

    def validate(self, data):
        user_from = self.context.get('view').request.user
        user_to = self.context.get('view').get_object()
        if user_from == user_to:
            raise serializers.ValidationError('User can not start conversation himself')
        return data

    def create(self, validated_data):
        user_from = validated_data.get('user_from')
        user_to = validated_data.get('user_to')
        files = validated_data.get('files', [])
        message = validated_data.get('message')
        start_conversation(
            user_from=user_from,
            user_to=user_to,
            files=files,
            message=message)
        return validated_data
