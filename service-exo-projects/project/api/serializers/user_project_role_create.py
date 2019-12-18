from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers, exceptions
from filestack import Filelink
from exo_role.models import ExORole

from utils.drf.relation import UserUUIDRelatedField
from team.models import Team
from utils.drf.project import CurrentProjectDefault

from ...models import UserProjectRole, ProjectRole
from .user_project_role import UserProjectSerializer
from ...tasks import RolesChangedTask


class ExOCollaboratorCreateSerializer(serializers.ModelSerializer):
    user = UserUUIDRelatedField(
        slug_field='uuid',
        queryset=get_user_model().objects.all())
    project_roles = serializers.SlugRelatedField(
        queryset=ExORole.objects.all(),
        many=True,
        slug_field='code')
    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        many=True,
        required=False)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserProjectRole
        fields = ['user', 'project_roles', 'teams', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = list(self.context.get('view').project.project_roles.all().values_list('code', flat=True))
        self.fields['project_roles'].queryset = ExORole.objects.filter(code__in=queryset)
        self.fields['teams'].queryset = self.context.get('view').project.teams.all()

    def create(self, validated_data):
        original_data = validated_data.copy()
        project = self.context.get('view').project
        exo_roles = validated_data.pop('project_roles', [])
        project_roles = ProjectRole.objects.filter(
            project=project,
            exo_role__in=exo_roles)
        teams = validated_data.pop('teams', None)
        for project_role in project_roles:
            validated_data['project_role'] = project_role
            if project_role.code == settings.EXO_ROLE_CODE_SPRINT_COACH:
                validated_data['teams'] = teams
            else:
                validated_data['teams'] = None
            super().create(validated_data)

        if not project.is_draft:
            RolesChangedTask().s(
                project_id=project.id,
                user_id=validated_data.get('user').id).apply_async()
        return original_data.get('user')

    def to_representation(self, value):
        return UserProjectSerializer(
            value,
            context=self.context).data


class ParticipantCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    email = serializers.CharField()
    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        many=True,
        required=False)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = UserProjectRole
        fields = ['name', 'email', 'teams', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teams'].queryset = self.context.get('view').project.teams.all()

    def create(self, validated_data):
        validated_data['project'] = self.context.get('view').project
        user_project_role = UserProjectRole.objects.create_participant(**validated_data)
        return user_project_role.user

    def to_representation(self, value):
        return UserProjectSerializer(
            value,
            context=self.context).data


class ParticipantCSVParseFileSerializer(serializers.Serializer):
    filename = serializers.CharField()

    def get_users_from_filestack(self, file_handler):
        content = file_handler.get_content()
        users = []
        for row in content.decode().splitlines():
            name, email = row.split(',')
            users.append({
                'name': name.strip(),
                'email': email.strip()})
        return users

    def validate(self, data):
        file_handler = Filelink(data.get('filename'))
        try:
            users = self.get_users_from_filestack(file_handler)
        except Exception:
            raise exceptions.ValidationError('Incorrect format')
        return users


class UserUploadSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()


class ParticipantCSVCreateSerializer(serializers.Serializer):
    users = UserUploadSerializer(many=True)
    project = serializers.HiddenField(
        default=CurrentProjectDefault())
    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        many=True,
        required=False)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    def create(self, validated_data):
        users = []

        for user in validated_data.get('users', []):
            user_data = {
                'name': user.get('name').strip(),
                'email': user.get('email').strip(),
                'teams': validated_data.get('teams', None),
                'project': validated_data.get('project'),
                'created_by': validated_data.get('created_by'),
            }
            user_role = UserProjectRole.objects.create_participant(**user_data)
            users.append(user_role)
        return users

    def to_representation(self, value):
        return UserProjectSerializer(
            value.user,
            context=self.context).data
