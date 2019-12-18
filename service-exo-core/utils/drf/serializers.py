import six
import pytz

from rest_framework import serializers

from django.contrib.auth import get_user_model

from utils.dates import string_to_timezone


class TimezoneField(serializers.Field):
    def to_representation(self, obj):
        return six.text_type(obj)

    def to_internal_value(self, data):
        try:
            return string_to_timezone(str(data))
        except pytz.exceptions.UnknownTimeZoneError:
            raise serializers.ValidationError('Unknown timezone')


class MultipleChoiceField(serializers.MultipleChoiceField):
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return [str(k) for k in value]


class UserCreatedBy(serializers.ModelSerializer):
    shortName = serializers.CharField(source='short_name')
    fullName = serializers.CharField(source='full_name')
    profilePictures = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['shortName', 'fullName', 'email', 'profilePictures', 'pk']

    def get_profilePictures(self, obj):
        images = []

        for width, height in obj._meta.get_field('profile_picture').thumbnails:
            value = {}
            value['width'] = width
            value['height'] = height
            value['url'] = obj.profile_picture.get_thumbnail_url(width, height)
            images.append(value)
        return images


class EmptySerializer(serializers.Serializer):
    pass
