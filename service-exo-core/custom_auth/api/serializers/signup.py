from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework import serializers

from exo_accounts.models import EmailAddress
from utils.segment import SegmentAnalytics


UserModel = get_user_model()


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def validate_email(self, value):
        email = UserModel._default_manager.normalize_email(value)
        user = self.context.get('invitation').user
        validated, code = EmailAddress.objects.check_email(
            user=user,
            email=email,
        )
        if not validated:
            raise serializers.ValidationError(
                settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, ''))
        return value

    def validate(self, attrs):
        invitation = self.context.get('invitation')
        invitation.can_be_accepted(invitation.user, raise_errors=True)
        return attrs

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        invitation = self.context.get('invitation')
        invitation.accept(invitation.user, email=email, password=password)

        SegmentAnalytics.event(
            user=invitation.user,
            category=settings.INSTRUMENTATION_ONBOARDING_CATEGORY,
            event=settings.INSTRUMENTATION_EVENT_STARTED,
            entry_point=settings.INSTRUMENTATION_USER_ENTRY_POINT_JOIN_US,
        )

        return authenticate(
            username=invitation.user.email,
            password=password,
        )
