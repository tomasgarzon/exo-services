import six
import pytz

from rest_framework import serializers

from utils.dates import string_to_timezone


class TimezoneField(serializers.Field):
    def to_representation(self, obj):
        return six.text_type(obj)

    def to_internal_value(self, data):
        try:
            return string_to_timezone(str(data))
        except pytz.exceptions.UnknownTimeZoneError:
            raise serializers.ValidationError('Unknown timezone')
