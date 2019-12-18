from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings

from files.api.serializers.uploaded_file import UploadedFileSerializer

from ...models import Opportunity
from ...tasks import OpportunityMessageReceivedTask


class StartConversationSerializer(serializers.Serializer):
    files = UploadedFileSerializer(many=True, required=False)
    message = serializers.CharField()

    def create(self, validated_data):
        opportunity = validated_data.get('opportunity')
        message = validated_data.get('message')
        files = validated_data.get('files', [])
        user_from = validated_data.get('user_from')
        opportunity.start_conversation(user_from, message, files)
        return opportunity


class StartConversationApplicantSerializer(serializers.Serializer):
    files = UploadedFileSerializer(many=True, required=False)
    message = serializers.CharField()

    def create(self, validated_data):
        opportunity = validated_data.get('opportunity')
        user_to = validated_data.get('user_to')
        message = validated_data.get('message')
        files = validated_data.get('files', [])
        user_from = validated_data.get('user_from')
        opportunity.start_conversation(
            user_from, message, files,
            user_to=user_to)
        return opportunity


class FirstMessageConversation(serializers.Serializer):
    message = serializers.CharField()
    created_by_uuid = serializers.UUIDField()
    other_user_uuid = serializers.UUIDField()
    opportunity_uuid = serializers.UUIDField()

    def validate_opportunity_uuid(self, value):
        try:
            Opportunity.objects.get(uuid=value)
        except Opportunity.DoesNotExist:
            raise serializers.ValidationError("Opportunity Does not exist")
        return value

    def validate_created_by_uuid(self, value):
        try:
            get_user_model().objects.get(uuid=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User Does not exist")
        return value

    def validate_other_user_uuid(self, value):
        try:
            get_user_model().objects.get(uuid=value)
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User Does not exist")
        return value

    def create(self, validated_data):
        opp = Opportunity.objects.get(
            uuid=validated_data.get('opportunity_uuid'))
        if not settings.POPULATOR_MODE:
            OpportunityMessageReceivedTask().s(
                pk=opp.pk,
                message=validated_data.get('message'),
                created_by=validated_data.get('created_by_uuid'),
                other_user=validated_data.get('other_user_uuid'),
            ).apply_async()
        return opp
