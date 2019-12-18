from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers

from badge.api.serializers.badge import UserBadgeSerializer
from custom_auth.helpers import UserProfileWrapper
from consultant.api.serializers.consultant_public import ConsultantPublicSerializer
from utils.drf.serializers import TimezoneField

from .profile_picture import UserProfilePictureSerializer
from .social_network import SocialNetworkSerializer


class ProfilePublicSerializer(serializers.ModelSerializer):
    badges_activity = UserBadgeSerializer(many=True, source='get_badges')
    consultant = ConsultantPublicSerializer()
    profile_pictures = UserProfilePictureSerializer(many=True)
    social_networks = serializers.SerializerMethodField()
    timezone = TimezoneField()
    is_staff = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'about_me',
            'badges_activity',
            'bio_me',
            'consultant',
            'date_joined',
            'full_name',
            'profile_pictures',
            'slug',
            'social_networks',
            'location',
            'timezone',
            'uuid',
            'user_title',
            'user_position',
            'is_staff',
            'pk',
            'place_id',
        ]

    def get_timezone(self, obj):
        return obj.timezone.zone if obj.timezone else None

    def get_social_networks(self, obj):
        obj.initialize_social_networks()
        social_networks = []

        for _, name in settings.EXO_ACCOUNTS_CH_SOCIAL_NETWORK:
            social = getattr(obj, name.lower())
            if social.value:
                social_networks.append(social)

        return SocialNetworkSerializer(social_networks, many=True).data

    def get_is_staff(self, obj):
        user_wrapper = UserProfileWrapper(obj)
        return user_wrapper.is_openexo_member


class ProfilePublicOwnUser(ProfilePublicSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'about_me',
            'badges_activity',
            'bio_me',
            'consultant',
            'date_joined',
            'full_name',
            'profile_pictures',
            'slug',
            'social_networks',
            'location',
            'timezone',
            'uuid',
            'user_title',
            'user_position',
            'is_staff',
            'pk',
            'place_id',
            'phone',
            'short_name',
        ]
