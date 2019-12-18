from rest_framework import serializers

from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            'email', 'uuid', 'password',
            'is_staff', 'is_superuser', 'is_active']
