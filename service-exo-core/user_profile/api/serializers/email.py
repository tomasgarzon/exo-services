from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers

from exo_accounts.models import EmailAddress

UserModel = get_user_model()


class ChangeEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        model = UserModel
        fields = ('email', )

    def validate_email(self, value):
        email = UserModel._default_manager.normalize_email(value)
        user = self.instance
        validated, code = EmailAddress.objects.check_email(
            user=user,
            email=email,
        )
        if not validated:
            raise serializers.ValidationError(
                settings.EXO_ACCOUNTS_EMAIL_VALIDATION.get(code, ''))
        return value

    def update(self, instance, validated_data):
        email = validated_data.get('email')
        EmailAddress.objects.change_user_email(
            user_from=self.context.get('request').user,
            user=instance,
            email=email,
        )
        return instance
