from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers
from auth_uuid.utils.user_wrapper import UserWrapper
from exo_role.api.serializers import CategoryExORoleSerializer

from utils.drf.user import UserSerializer
from team.api.serializers.user_in_team import UserInTeamSerializer

from ...models import UserProjectRole


class ExOCollaboratorSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    project_role = serializers.CharField(
        source='project_role.exo_role.code')
    teams = UserInTeamSerializer(many=True)

    class Meta:
        model = UserProjectRole
        fields = ['user', 'project_role', 'active', 'teams', 'pk']

    def get_user(self, obj):
        user_wrapper = UserWrapper(user=obj.user)
        return UserSerializer(user_wrapper).data


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    project_role = serializers.CharField(
        source='project_role.exo_role.code')
    teams = UserInTeamSerializer(many=True)

    class Meta:
        model = UserProjectRole
        fields = ['user', 'project_role', 'teams', 'active', 'pk']

    def get_user(self, obj):
        if hasattr(obj.user, 'participant'):
            user_wrapper = obj.user.participant
        else:
            user_wrapper = UserWrapper(user=obj.user)
        return UserSerializer(user_wrapper).data


class UserProjectSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    project_roles = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['user', 'project_roles', 'teams', 'actions']

    def get_user(self, obj):
        if hasattr(obj, 'participant'):
            user_wrapper = obj.participant
        else:
            user_wrapper = UserWrapper(user=obj)
        return UserSerializer(user_wrapper).data

    def get_project_roles(self, obj):
        project = self.context.get('view').project
        queryset = obj.user_project_roles.filter(project_role__project=project).exo_roles()
        return CategoryExORoleSerializer(queryset, many=True).data

    def get_teams(self, obj):
        project = self.context.get('view').project
        teams = obj.user_team_roles.filter(team__project=project)
        return UserInTeamSerializer(teams, many=True).data

    def get_actions(self, obj):
        project = self.context.get('view').project
        return project.user_actions_for_user(
            self.context.get('request').user, obj)


class UserNoTeamProjectSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    project_roles = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['user', 'project_roles']

    def get_user(self, obj):
        if hasattr(obj, 'participant'):
            user_wrapper = obj.participant
        else:
            user_wrapper = UserWrapper(user=obj)
        return UserSerializer(user_wrapper).data

    def get_project_roles(self, obj):
        COACH_OR_PARTICIPANT = [
            settings.EXO_ROLE_CODE_SPRINT_COACH,
            settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        ]
        queryset = obj.user_project_roles.filter(
            project_role__code__in=COACH_OR_PARTICIPANT).exo_roles()
        return CategoryExORoleSerializer(queryset, many=True).data
