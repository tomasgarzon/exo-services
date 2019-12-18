from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    email = serializers.CharField()
    short_name = serializers.CharField()
    full_name = serializers.CharField()
    profile_url = serializers.CharField()
    profile_pictures = serializers.ListField(source='profile_picture')
    user_title = serializers.CharField()
