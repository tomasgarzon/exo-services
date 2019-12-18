from rest_framework import serializers

from ...conf import settings


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        style={'input_type': 'password'},
    )


class PasswordRetypeSerializer(PasswordSerializer):
    re_new_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'password_mismatch': settings.USER_PROFILE_PASSWORD_MISMATCH_ERROR,
    }

    def validate(self, attrs):
        attrs = super(PasswordRetypeSerializer, self).validate(attrs)
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError(self.error_messages['password_mismatch'])
        return attrs
