from django.contrib.auth import get_user_model

from rest_framework import serializers
from exo_role.models import ExORole, Category

from utils.drf.relations import UserUUIDRelatedField

from ...models import Job


class JobCreateSerializer(serializers.ModelSerializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    exo_role = serializers.SlugRelatedField(
        slug_field='code',
        queryset=ExORole.objects.all())
    category = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Category.objects.all())
    url = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False)

    class Meta:
        model = Job
        read_only_fields = ['id', 'uuid']
        fields = '__all__'
