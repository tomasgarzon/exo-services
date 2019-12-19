from rest_framework import serializers

from django.contrib.auth import get_user_model

from custom_auth.helpers import UserProfileWrapper
from user_profile.api.serializers.certification import CertificationCredentialConsultantRoleSerializer

User = get_user_model()


class FollowerSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['profile_picture', 'get_full_name', 'profile_url', 'certifications']

    def get_profile_picture(self, obj):
        images = []
        for width, height in obj._meta.get_field('profile_picture').thumbnails:
            value = (
                (width, height),
                obj.profile_picture.get_thumbnail_url(width, height),
            )
            images.append(value)
        return images

    def get_profile_url(self, obj):
        return UserProfileWrapper(obj).profile_slug_url

    def get_certifications(self, obj):
        if obj.is_consultant:
            return CertificationCredentialConsultantRoleSerializer(
                obj.consultant.get_certificates(), many=True).data
        return []
