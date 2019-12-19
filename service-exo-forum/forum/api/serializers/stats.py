from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['profile_picture', 'short_name', 'full_name', 'id']

    def get_profile_picture(self, obj):
        images = []
        for width, height in obj._meta.get_field('profile_picture').thumbnails:
            value = (
                (width, height),
                obj.profile_picture.get_thumbnail_url(width, height),
            )
            images.append(value)
        return images


class ForumUserSerializer(serializers.Serializer):

    user = UserSerializer()
    total_answers = serializers.IntegerField()
