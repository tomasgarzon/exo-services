from rest_framework import serializers

from utils.drf.project import CurrentProjectDefault
from utils.models import Stream

from ...models import Team
from .stream import StreamSerializer
from .team_role import UserTeamRoleSerializer


class TeamSerializer(serializers.ModelSerializer):
    stream = StreamSerializer()
    users = UserTeamRoleSerializer(many=True, source='user_team_roles')
    total_users = serializers.SerializerMethodField()
    user_actions = serializers.SerializerMethodField()

    class Meta:
        model = Team
        read_only_fields = ['pk', 'uuid']
        fields = [
            'uuid', 'pk', 'name', 'stream', 'users', 'total_users',
            'user_actions', 'image']

    def get_total_users(self, obj):
        return obj.members.count()

    def get_user_actions(self, obj):
        return obj.user_actions(self.context.get('request').user)


class TeamCreateSerializer(serializers.ModelSerializer):
    stream = serializers.PrimaryKeyRelatedField(queryset=Stream.objects.all())
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    project = serializers.HiddenField(
        default=CurrentProjectDefault())

    class Meta:
        model = Team
        fields = ['name', 'stream', 'created_by', 'project', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stream'].queryset = self.context.get('view').project.streams.all()

    def to_representation(self, value):
        return TeamSerializer(value, context=self.context).data
