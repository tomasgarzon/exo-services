from rest_framework import serializers
from exo_role.api.serializers import CategoryExORoleSerializer

from ...models import UserTeamRole


class UserInTeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='team.name')
    exo_role = CategoryExORoleSerializer(source='team_role.exo_role')
    team_pk = serializers.IntegerField(source='team.pk')

    class Meta:
        model = UserTeamRole
        fields = ['name', 'exo_role', 'pk', 'team_pk']
