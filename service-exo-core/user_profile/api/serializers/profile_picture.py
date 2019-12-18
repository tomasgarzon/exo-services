from rest_framework import serializers


class UserProfilePictureSerializer(serializers.Serializer):
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    url = serializers.CharField()
