from django.conf import settings

from rest_framework import serializers
from auth_uuid.utils.user_wrapper import UserWrapper

from utils.drf.user import UserSerializer

from ...models import ApplicantFeedback


class FeedbackApplicantSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantFeedback
        fields = [
            'comment', 'created_by',
            'status',
            'explained', 'collaboration', 'communication',
            'recommendation']

    def get_created_by(self, obj):
        user_wrapper = UserWrapper(user=obj.created_by)
        return UserSerializer(user_wrapper).data

    def validate(self, validated_data):
        applicant = self.context.get('view').get_object()
        user_from = self.context.get('request').user
        action = settings.OPPORTUNITIES_ACTION_CH_FEEDBACK
        applicant.can_do_actions(user_from, action)
        return validated_data

    def create(self, validated_data):
        user_from = validated_data.pop('user_from')
        applicant = validated_data.pop('applicant')
        applicant_feedback = applicant.give_feedback(
            user_from,
            **validated_data)
        return applicant_feedback
