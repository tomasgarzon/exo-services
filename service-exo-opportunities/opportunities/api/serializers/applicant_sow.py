from rest_framework import serializers

from utils.drf.serializers import TimezoneField

from ...models import ApplicantSow
from ...signals_define import send_message_to_conversation


class ApplicantEditSowSerializer(serializers.ModelSerializer):
    timezone = TimezoneField(required=False)

    class Meta:
        model = ApplicantSow
        fields = [
            'title', 'description', 'mode', 'location', 'place_id',
            'location_url', 'entity', 'budgets',
            'start_date', 'end_date', 'start_time', 'timezone',
            'duration_unity', 'duration_value',
        ]

    def update(self, instance, cleaned_data):
        user_from = cleaned_data.pop('user_from')
        applicant = cleaned_data.pop('applicant')
        applicant.update_sow(user_from, **cleaned_data)
        instance.refresh_from_db()
        return instance


class RequesterEditSowSerializer(serializers.Serializer):
    response_message = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True)
    sow = ApplicantEditSowSerializer()

    def update(self, instance, validated_data):
        user_from = validated_data.get('user_from')
        serializer = ApplicantEditSowSerializer(
            instance.sow, self.initial_data.get('sow'))
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=user_from,
            applicant=instance)
        send_message_to_conversation.send(
            sender=instance.__class__,
            applicant=instance,
            user_from=user_from,
            message=validated_data.get('response_message'))
        return instance


class InitialApplicantSowSerializer(serializers.Serializer):
    tax_id = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    entity = serializers.CharField(required=False)
    mode = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    place_id = serializers.CharField(required=False)
    location_url = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    budgets = serializers.JSONField(required=False)
    duration_unity = serializers.CharField(required=False)
    duration_value = serializers.IntegerField(required=False)
