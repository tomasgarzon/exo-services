from django.conf import settings

from rest_framework import serializers

from .applicant_sow import ApplicantEditSowSerializer


class AssignOpportunitySerializer(serializers.Serializer):
    response_message = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True)
    sow = ApplicantEditSowSerializer()

    def validate(self, data):
        applicant = self.context.get('view').get_object()
        applicant.can_do_actions(
            self.context.get('request').user,
            settings.OPPORTUNITIES_ACTION_CH_ASSIGN)
        return data

    def create(self, validated_data):
        applicant = validated_data.get('applicant')
        instance = applicant.opportunity
        instance.assign(
            user_from=validated_data.get('user_from'),
            applicant=applicant,
            response_message=validated_data.get('response_message'),
            **validated_data.get('sow'))
        return instance


class RejectOpportunitySerializer(serializers.Serializer):
    response_message = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    def validate(self, data):
        applicant = self.context.get('view').get_object()
        applicant.can_do_actions(
            self.context.get('request').user,
            settings.OPPORTUNITIES_ACTION_CH_REJECT)
        return data

    def create(self, validated_data):
        applicant = validated_data.get('applicant')
        instance = applicant.opportunity
        instance.reject(
            user_from=validated_data.get('user_from'),
            applicant=validated_data.get('applicant'),
            response_message=validated_data.get('response_message'),)
        return instance
