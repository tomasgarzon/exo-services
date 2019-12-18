from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import serializers
from auth_uuid.utils.user_wrapper import UserWrapper

from utils.drf.relations import UserUUIDRelatedField
from utils.drf.user import UserSerializer

from ...models import UserTagged


class UserUUIDSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['uuid']


class UserUUIDPermSerializerMixin(serializers.Serializer):
    perm = serializers.ChoiceField(
        choices=settings.AUTH_USER_ALL_PERMISSIONS,
        required=True)


class UserUUIDAddPermSerializer(UserUUIDPermSerializerMixin):

    def update(self, instance, validated_data):
        perm = validated_data.get('perm')
        permission = get_object_or_404(Permission, codename=perm)
        instance.user_permissions.add(permission)
        return validated_data


class UserUUIDRemovePermSerializer(UserUUIDPermSerializerMixin):

    def update(self, instance, validated_data):
        perm = validated_data.get('perm')
        permission = get_object_or_404(Permission, codename=perm)
        instance.user_permissions.remove(permission)
        return validated_data


class UserTaggedSerializer(serializers.ModelSerializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())

    class Meta:
        model = UserTagged
        fields = ['user']

    def to_representation(self, value):
        user = value.user
        user_wrapper = UserWrapper(user=user)
        return UserSerializer(user_wrapper).data
