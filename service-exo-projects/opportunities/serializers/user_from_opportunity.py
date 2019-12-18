from django.contrib.auth import get_user_model

from rest_framework import serializers
from exo_role.models import ExORole

from utils.drf.relation import UserUUIDRelatedField
from project.models import UserProjectRole
from jobs.models import Job

from ..models import OpportunityProjectRole


class AddUserFromOpportunitySerializer(serializers.Serializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    exo_role = serializers.SlugRelatedField(
        slug_field='code',
        queryset=ExORole.objects.all())
    opportunity_uuid = serializers.UUIDField()
    user_from = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())

    def create(self, validated_data):
        project = validated_data.get('project')
        project_role = project.project_roles.filter(
            exo_role=validated_data.get('exo_role')).first()
        if not project_role:
            return None
        instance = UserProjectRole.objects.create(
            project_role=project_role,
            created_by=validated_data.get('user_from'),
            user=validated_data.get('user'),
        )
        OpportunityProjectRole.objects.create(
            user_project_role=instance,
            opportunity_uuid=validated_data.get('opportunity_uuid'))
        try:
            job = instance.job
            job.delete()
            Job.objects.update_or_create(user_project_role=instance)
        except Exception:
            pass
        return instance
