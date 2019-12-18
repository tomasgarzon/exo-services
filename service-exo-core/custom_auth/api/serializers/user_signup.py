from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSignupSerializer(serializers.ModelSerializer):
    short_name = serializers.CharField(required=True)
    uuid = serializers.UUIDField(required=True)
    email = serializers.EmailField(required=True)
    user_from = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    created = serializers.BooleanField(required=False)

    class Meta:
        model = get_user_model()
        read_only_fields = ['pk']
        fields = [
            'user_from',
            'uuid',
            'short_name',
            'full_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'password',
            'pk',
            'created'
        ]

    def create(self, validated_data):
        copy_data = validated_data.copy()
        email = validated_data.pop('email')
        user, created = self.Meta.model.objects.get_or_create(
            email=email,
            defaults=validated_data,
            user_from=validated_data.pop('user_from'),
        )
        copy_data['pk'] = user.pk
        copy_data['uuid'] = user.uuid.__str__()
        copy_data['created'] = created
        return copy_data
