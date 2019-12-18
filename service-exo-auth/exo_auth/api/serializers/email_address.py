from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import serializers

from ...models import EmailAddress


class ValidateEmailSerializerMixin(serializers.Serializer):

    permission_required = settings.EXO_AUTH_PERMS_USER_EDIT

    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        read_only=False,
    )
    email = serializers.EmailField()

    def validate_user(self, value):
        request_user = self.context.get('request').user
        user = value

        if not request_user.has_perm(self.permission_required, user):
            raise PermissionDenied

        return value


class ValidateEmailSerializer(ValidateEmailSerializerMixin):

    def validate(self, attrs):
        user = attrs.get('user')
        email = attrs.get('email')

        validated, code = EmailAddress.objects.check_email(user, email)
        message = settings.EXO_AUTH_EMAIL_VALIDATION.get(code, '')

        if not validated:
            raise ValidationError(message)

        return attrs


class ResendEmailAddressEmailSerializer(ValidateEmailSerializer):

    def validate(self, attrs):
        user = attrs.get('user')
        email = attrs.get('email')

        email_address = EmailAddress.objects.filter(
            user=user,
            email=email,
            verified_at__isnull=False,
        )

        if email_address.exists():
            raise ValidationError('Email already verified')
        else:
            try:
                EmailAddress.objects.get(
                    user=user,
                    email=email,
                )
            except EmailAddress.DoesNotExist:
                raise ValidationError('Email already deleted')

        return attrs


class DiscardEmailSerializer(serializers.Serializer):

    permission_required = settings.EXO_AUTH_PERMS_USER_EDIT

    email = serializers.PrimaryKeyRelatedField(
        queryset=EmailAddress.objects.all(),
        read_only=False,
    )
    verif_key = serializers.CharField()

    def validate_email(self, value):
        user = self.context.get('request').user
        email = value

        if not user.has_perm(self.permission_required, email.user):
            raise PermissionDenied

        return value

    def validate(self, attrs):
        email = attrs.get('email')
        verif_key = attrs.get('verif_key')
        verified, message = email.verify_discard(verif_key, False)
        if not verified:
            raise ValidationError(message)

        return attrs


class CheckEmailSerializer(ValidateEmailSerializerMixin):

    def validate_email(self, value):

        if get_user_model().objects.filter(email__iexact=value):
            raise ValidationError('This email is already in use')

        return value
