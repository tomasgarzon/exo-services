from django.conf import settings
from django.core import signing
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import get_object_or_404
from password_reset.views import Reset
from rest_framework import serializers

from ...forms.reset_password import UserResetPasswordForm


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = UserResetPasswordForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors.get('email'))

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)


class PasswordChangeSerializer(
    serializers.Serializer,
    Reset
):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    form_error_messages = {
        'password_mismatch': "Passwords don't match.",
    }

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = False
        self.logout_on_password_change = False

        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')

        try:
            pk = signing.loads(
                kwargs.get('data').get('token'),
                max_age=self.get_token_expires(),
                salt=self.salt,
            )
            self.user = get_object_or_404(get_user_model(), pk=pk)
        except signing.BadSignature:
            self.user = None
        except AttributeError:
            self.user = None  # Swagger need

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate_new_password1(self, value):
        password_validation.validate_password(value, self.user)
        return value

    def validate(self, attrs):
        if self.user:
            self.set_password_form = self.set_password_form_class(
                user=self.user,
                data=attrs,
            )
        else:
            raise serializers.ValidationError('Invalid token')

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            update_session_auth_hash(self.request, self.user)
