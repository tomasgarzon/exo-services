from rest_framework import serializers
from exo_role.api.serializers import CategoryExORoleSerializer

from utils.drf.project import CurrentProjectDefault

from ...models import ProjectTeamRole


class TeamRoleSerializer(serializers.ModelSerializer):
    project = serializers.HiddenField(
        default=CurrentProjectDefault())
    exo_role = CategoryExORoleSerializer()

    class Meta:
        model = ProjectTeamRole
        fields = ['pk', 'project', 'exo_role']


class TeamRoleSimpleSerializer(serializers.ModelSerializer):
    exo_role = CategoryExORoleSerializer()

    class Meta:
        model = ProjectTeamRole
        fields = ['exo_role', 'pk']
