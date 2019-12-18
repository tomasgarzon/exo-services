from django.contrib.auth import get_user_model

from rest_framework import serializers

from ...models import EmailAddress

User = get_user_model()


class EmailAddressSerializer(serializers.Serializer):
    created = serializers.DateTimeField()
    modified = serializers.DateTimeField()
    email = serializers.CharField()
    verif_key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    verified_at = serializers.DateTimeField(required=False)
    remote_addr = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    remote_host = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_primary = serializers.BooleanField()
    type_email = serializers.CharField()


class MigrateUserSeriailzer(serializers.Serializer):

    email = serializers.CharField()
    password = serializers.CharField(required=False, allow_blank=True)
    password_updated = serializers.BooleanField()
    uuid = serializers.UUIDField()
    date_joined = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    emails = EmailAddressSerializer(many=True)

    def create(self, validated_data):
        uuid = validated_data.get('uuid')
        email = validated_data.get('email')
        user, _ = User.objects.get_or_create(email=email, defaults={'id': uuid})

        for key, value in validated_data.items():
            if key != 'emails':
                setattr(user, key, value)
        user.save()

        for email_data in validated_data.get('emails', []):
            email = email_data.get('email')
            email_address, _ = EmailAddress.objects.get_or_create(
                user=user,
                email=email)
            for key, value in email_data.items():
                setattr(email_address, key, value)
            email_address.save()
        return user
