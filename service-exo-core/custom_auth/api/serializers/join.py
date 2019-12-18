from django.contrib.auth import get_user_model, authenticate
from django.conf import settings

from rest_framework import serializers

from exo_accounts.models import EmailAddress
from consultant.models import Consultant
from consultant.tasks import CreateHubspotContactTask
from utils.drf.mixins.recaptcha_serializer import RecaptchaSerializerMixin


UserModel = get_user_model()
STEPS_NAMES = settings.REGISTRATION_STEPS_NAMES


class JoinUsSerializer(RecaptchaSerializerMixin, serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(allow_blank=False)
    password = serializers.CharField(
        style={'input_type': 'password'},
        required=False)
    entry_point = serializers.JSONField()
    recaptcha = serializers.CharField()
    interested_join = serializers.CharField(required=False, allow_blank=True)
    custom_text = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)

    def validate_email(self, value):
        email = UserModel._default_manager.normalize_email(value)
        email_used = EmailAddress.objects.filter(
            email=email,
            user__consultant__isnull=False).exists()
        if email_used:
            raise serializers.ValidationError('This email is already used')
        return value

    def create(self, validated_data, default_step=2):
        email = validated_data.get('email')
        password = validated_data.get('password')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        entry_point = validated_data.get('entry_point')
        custom_text = validated_data.get('custom_text', None)
        skip_steps = []
        if password:
            skip_steps = [STEPS_NAMES[default_step][0]]
        else:
            password = get_user_model().objects.make_random_password()
        consultant = Consultant.objects.create_consultant(
            short_name=first_name,
            full_name='{} {}'.format(first_name, last_name),
            email=email,
            custom_text=custom_text,
            registration_process=True,
            skip_steps=skip_steps,
            entry_point=entry_point,
            password=password,
        )
        user = consultant.user

        if not settings.POPULATOR_MODE:
            CreateHubspotContactTask().s(
                first_name=validated_data.get('first_name'),
                last_name=validated_data.get('last_name'),
                email=validated_data.get('email'),
                entry_point=entry_point.get('name', ''),
                city=entry_point.get('city', ''),
                interested_join=validated_data.get('interested_join')).apply_async()
        return authenticate(
            username=user.email,
            password=password,
        )
