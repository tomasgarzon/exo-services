from rest_framework import serializers

from django.contrib.auth.models import Group

from .external_user import UserSerializer


class GroupSerializer(serializers.ModelSerializer):

    user_set = UserSerializer(many=True)

    class Meta:
        model = Group
        fields = ['name', 'user_set']
