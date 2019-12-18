from rest_framework import serializers
from django.contrib.auth import get_user_model
from auth_uuid.utils.user_wrapper import UserWrapper


class UserSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    email = serializers.CharField()
    short_name = serializers.CharField()
    full_name = serializers.CharField()
    slug = serializers.CharField()
    profile_url = serializers.CharField()
    profile_pictures = serializers.ListField(source='profile_picture')
    user_title = serializers.CharField()

    def __init__(self, instance=None, **kwargs):
        if isinstance(instance, get_user_model()):
            instance = UserWrapper(user=instance)
        super().__init__(instance, **kwargs)
