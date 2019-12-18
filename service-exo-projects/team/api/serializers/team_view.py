from rest_framework import serializers

from exo_role.api.serializers import CategoryExORoleSerializer

from ...models import Team


class TeamViewSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    group_uuid = serializers.SerializerMethodField()

    class Meta:
        model = Team
        read_only_fields = ['pk', 'uuid']
        fields = ['uuid', 'pk', 'name', 'stream', 'image', 'roles', 'group_uuid']

    def get_roles(self, obj):
        user = self.context.get('request').user
        queryset = obj.user_team_roles.filter(user=user).exo_roles()
        return CategoryExORoleSerializer(queryset, many=True).data

    def get_group_uuid(self, obj):
        try:
            return obj.opportunity_group.group_uuid
        except AttributeError:
            return None
