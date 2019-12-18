from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group

from rest_framework import serializers

from ...jwt_helpers import _build_jwt


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ['name']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):

    user_permissions = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    groups = GroupSerializer(many=True)

    class Meta:
        model = get_user_model()
        exclude = [
            'password', 'date_joined',
        ]

    def get_token(self, obj):
        return _build_jwt(obj)

    def get_user_permissions(self, obj):
        return obj.user_permissions.values_list('codename', flat=True)


class UserUUIDSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = [
            'uuid', 'email',
            'groups',
            'is_staff', 'is_superuser', 'is_active']
