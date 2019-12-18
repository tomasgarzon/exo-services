from django.contrib.auth import get_user_model

from rest_framework import serializers

from custom_auth.helpers import UserProfileWrapper
from utils.drf.serializers import TimezoneField


class UserPublicProfile(serializers.ModelSerializer):
    url_view = serializers.SerializerMethodField()
    timezone = TimezoneField()

    class Meta:
        model = get_user_model()
        fields = [
            'short_name',
            'full_name',
            'email',
            'location',
            'timezone',
            'about_me',
            'short_me',
            'url_view',
        ]

    def get_url_view(self, obj):
        return UserProfileWrapper(obj).profile_slug_url
