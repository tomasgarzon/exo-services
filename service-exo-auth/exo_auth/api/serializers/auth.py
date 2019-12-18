from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

from ...models import EmailAddress

UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = authenticate(
                username=UserModel._default_manager.normalize_email(username),
                password=password,
            )
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate_username(self, value):
        try:
            email = EmailAddress.objects.get(
                email=UserModel._default_manager.normalize_email(value),
            )

            if not email.is_verified:
                raise serializers.ValidationError(
                    'Pending verification. You can log in with your previous email.',
                )

        except EmailAddress.DoesNotExist:
            raise serializers.ValidationError(
                "This email address doesn't exist",
            )
        return value

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = None
        user = self._validate_username(username, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Email and password do not match')
            raise exceptions.ValidationError(msg)

        attrs['user'] = user
        return attrs


class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    token = serializers.CharField()
    url = serializers.CharField()
