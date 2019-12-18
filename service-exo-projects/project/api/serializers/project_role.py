from rest_framework import serializers

from exo_role.api.serializers import CategoryExORoleSerializer
from exo_role.models import ExORole

from utils.drf.project import CurrentProjectDefault

from ...models import ProjectRole


class ProjectRoleSerializer(serializers.ModelSerializer):
    exo_role = CategoryExORoleSerializer()
    project = serializers.HiddenField(
        default=CurrentProjectDefault())

    class Meta:
        model = ProjectRole
        fields = ['exo_role', 'project']


class ProjectCreateRoleSerializer(serializers.ModelSerializer):
    exo_role = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        slug_field='code')
    project = serializers.HiddenField(
        default=CurrentProjectDefault())

    class Meta:
        model = ProjectRole
        fields = ['exo_role', 'project', 'role', 'code']
