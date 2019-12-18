from django.contrib.auth import get_user_model

from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from core.models import Language
from utils.drf.serializers import TimezoneField
from custom_auth.tasks.user_location import UserLocationTask


class SummarySerializer(serializers.ModelSerializer):

    profile_picture = Base64ImageField(required=False)
    languages = serializers.PrimaryKeyRelatedField(
        queryset=Language.objects.all(),
        many=True,
        required=False,
    )
    location = serializers.CharField(required=False)
    place_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    timezone = TimezoneField(required=False)

    class Meta:
        model = get_user_model()
        fields = [
            'short_name',
            'full_name',
            'location',
            'place_id',
            'timezone',
            'profile_picture',
            'languages'
        ]

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        if instance.is_consultant and validated_data.get('languages'):
            instance.consultant.languages.clear()
            instance.consultant.languages.add(*validated_data.get('languages'))
        instance.languages = validated_data.get('languages', [])
        UserLocationTask().s(
            user_id=instance.pk).apply_async()
        return instance
