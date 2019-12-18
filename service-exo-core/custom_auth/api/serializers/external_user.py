from rest_framework import serializers

from django.contrib.auth import get_user_model

from ...helpers import UserProfileWrapper


class UserSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    disable_notification_url = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'email',
            'uuid',
            'short_name',
            'full_name',
            'thumbnail',
            'has_signed_marketplace_agreement',
            'disable_notification_url',
        ]
        ref_name = 'UserSerializerExternal'

    def get_thumbnail(self, obj):
        return obj.profile_picture.get_thumbnail_url()

    def get_disable_notification_url(self, obj):
        return UserProfileWrapper(obj).account_url
