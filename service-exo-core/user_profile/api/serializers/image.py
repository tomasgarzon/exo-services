from django.contrib.auth import get_user_model

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField


class ImageProfileSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField()

    class Meta:
        model = get_user_model()
        fields = ('profile_picture',)
