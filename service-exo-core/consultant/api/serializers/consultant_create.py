from django.contrib.auth import get_user_model

from rest_framework import serializers

from exo_accounts.utils.util import normalize_email

from ...models import Consultant


class ConsultantSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField()
    coins = serializers.IntegerField(
        required=False,
    )
    waiting_list = serializers.BooleanField(
        required=False,
    )
    custom_text = serializers.CharField(
        required=False,
    )

    class Meta:
        fields = ['email', 'name', 'coins', 'waiting_list', 'custom_text']

    model = Consultant

    def validate_email(self, value):
        value = normalize_email(value)
        user = get_user_model().objects.filter(email=value)
        if user.exists():
            user = user.get()
            if user.is_consultant:
                raise serializers.ValidationError('A consultant already exists with this email')
        return value

    def create(self, validated_data):
        skip_steps = []
        email = normalize_email(validated_data.get('email'))
        name = validated_data.get('name')
        custom_text = validated_data.get('custom_text')
        full_name = name
        short_name = name.split(' ')[0]

        consultant = self.model.objects.create_consultant(
            short_name=short_name,
            full_name=full_name,
            email=email,
            invite_user=validated_data.get('user_from'),
            registration_process=True,
            skip_steps=skip_steps,
            custom_text=custom_text,
            coins=validated_data.get('coins'),
            waiting_list=validated_data.get('waiting_list'),
        )

        return consultant


class ConsultantCreatedSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    user_id = serializers.IntegerField(source='user.pk')
    short_name = serializers.CharField(source='user.short_name')
    full_name = serializers.CharField(source='user.full_name')
    registration_url = serializers.SerializerMethodField()

    class Meta:
        model = Consultant
        fields = [
            'id', 'email', 'user_id', 'registration_url',
            'short_name', 'full_name']

    def get_registration_url(self, obj):
        return obj.registration_process.get_next_step_public_url()
