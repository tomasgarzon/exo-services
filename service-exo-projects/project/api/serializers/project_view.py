from rest_framework import serializers
from django.conf import settings
from exo_role.api.serializers import CategoryExORoleSerializer

from auth_uuid.utils.user_wrapper import UserWrapper

from team.api.serializers.stream import StreamSerializer
from team.api.serializers.team_view import TeamViewSerializer
from utils.permissions.objects import get_team_for_user
from utils.drf.user import UserSerializer

from ...models import Project
from .step import StepSerializer
from .project_settings import ProjectSettingsSerializer


class ViewProjectSerializer(serializers.ModelSerializer):
    settings = ProjectSettingsSerializer()
    streams = StreamSerializer(many=True)
    steps = StepSerializer(many=True)
    current_step = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    project_roles = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'pk', 'name', 'start', 'customer',
            'location', 'place_id', 'uuid',
            'streams', 'current_step',
            'status', 'template_name',
            'settings', 'steps', 'teams',
            'project_roles',
            'description',
            'creator',
        ]

    def get_current_step(self, obj):
        step = obj.current_step()
        if step:
            return step.pk

    def get_teams(self, obj):
        teams = get_team_for_user(obj, self.context.get('request').user)
        return TeamViewSerializer(teams, many=True, context=self.context).data

    def get_project_roles(self, obj):
        user = self.context.get('request').user
        exo_roles = user.user_project_roles.filter(
            project_role__project=obj).exo_roles()
        return CategoryExORoleSerializer(exo_roles, many=True).data

    def get_creator(self, obj):
        created_by = UserWrapper(user=obj.created_by)
        return UserSerializer(created_by).data


class ViewZoneProjectSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    chat_url = serializers.SerializerMethodField()
    advisor_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['url', 'name', 'chat_url', 'advisor_url']

    def get_url(self, obj):
        return obj.url_zone(self.context.get('request').user)

    def _get_team(self, obj):
        user = self.context.get('request').user
        teams = get_team_for_user(obj, user)
        if teams:
            team = teams.first()
        else:
            team = obj.teams.all().first()
        return team

    def get_chat_url(self, obj):
        team = self._get_team(obj)
        return settings.PROJECT_CHAT_URL.format(
            obj.id,
            team.id)

    def get_advisor_url(self, obj):
        team = self._get_team(obj)
        return settings.PROJECT_ADVISOR_URL.format(
            obj.id,
            team.id)
