from django.contrib.auth import get_user_model

from rest_framework import serializers
from exo_role.models import ExORole

from utils.drf.relation import UserUUIDRelatedField
from utils.drf.project import CurrentProjectDefault
from utils.drf.team import CurrentTeamDefault

from project.models import UserProjectRole
from ...models import UserTeamRole, ProjectTeamRole, Team
from .role import TeamRoleSimpleSerializer


class UserTeamRoleSerializer(serializers.ModelSerializer):
    uuid_user = serializers.UUIDField(source='user.uuid')
    role = TeamRoleSimpleSerializer(source='team_role')
    user_actions = serializers.SerializerMethodField()

    class Meta:
        model = UserTeamRole
        fields = ['uuid_user', 'role', 'active', 'pk', 'user_actions']

    def get_user_actions(self, obj):
        return obj.user_actions(self.context.get('request').user)


class UserTeamRoleCreateSerializer(serializers.ModelSerializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    team_role = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        slug_field='code')
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserTeamRole
        fields = ['user', 'team_role', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['team_role'].queryset = self.context.get('view').project.team_roles.all()

    def create(self, validated_data):
        project = self.context.get('view').project
        exo_role = validated_data.pop('team_role')
        team_role = ProjectTeamRole.objects.get(
            project=project,
            code=exo_role.code)
        validated_data['team_role'] = team_role
        return super().create(validated_data)


class UserMoveTeamSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    new_team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all())

    class Meta:
        model = UserTeamRole
        fields = ['new_team', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_team'].queryset = self.context.get('view').project.teams.all()

    def update(self, instance, validated_data):
        instance.team = validated_data.get('new_team')
        instance.save()
        return instance


class AssignProjectRolesToTeamSerializer(serializers.Serializer):
    project_roles = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        many=True,
        slug_field='code')
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    project = serializers.HiddenField(
        default=CurrentProjectDefault())
    team = serializers.HiddenField(
        default=CurrentTeamDefault())

    def create(self, validated_data):
        user_team_roles = []
        project = validated_data.get('project')
        team = validated_data.get('team')
        created_by = validated_data.get('created_by')
        exo_roles = validated_data.pop('project_roles', [])
        project_roles = UserProjectRole.objects.filter(
            project_role__project=project,
            project_role__exo_role__in=exo_roles)
        for user_project_role in project_roles:
            team_project_role = project.team_roles.get(
                code=user_project_role.project_role.code)
            user_team_role = UserTeamRole.objects.create(
                created_by=created_by,
                user=user_project_role.user,
                team=team,
                team_role=team_project_role)
            user_team_roles.append(user_team_role)
        return user_team_roles
