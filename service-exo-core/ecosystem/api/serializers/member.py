from rest_framework import serializers

from core.api.serializers.language import LanguageSerializer
from user_profile.api.serializers.profile_picture import UserProfilePictureSerializer

from ...models import Member


class MemberPublicSerializer(serializers.ModelSerializer):
    profile_pictures = UserProfilePictureSerializer(many=True)
    purpose = serializers.CharField(source='user.consultant.exo_profile.personal_mtp')
    languages = LanguageSerializer(many=True)

    class Meta:
        model = Member
        fields = [
            'certifications',
            'languages',
            'full_name',
            'location',
            'profile_pictures',
            'slug',
            'purpose',
        ]


class MemberSerializer(serializers.ModelSerializer):
    profile_pictures = UserProfilePictureSerializer(many=True)
    purpose = serializers.CharField(source='user.consultant.exo_profile.personal_mtp')

    class Meta:
        model = Member
        fields = [
            'full_name',
            'user_title',
            'location',
            'certifications',
            'profile_pictures',
            'slug',
            'purpose',
            'is_staff',
        ]
