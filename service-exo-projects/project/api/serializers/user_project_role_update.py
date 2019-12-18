from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers
from exo_role.models import ExORole

from team.models import Team

from ...models import UserProjectRole, ProjectRole
from ...tasks import RolesChangedTask


class ExOCollaboratorUpdateSerializer(serializers.ModelSerializer):
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
        model = get_user_model()
        fields = ['project_roles', 'teams', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = list(self.context.get('view').project.project_roles.all().values_list('code', flat=True))
        self.fields['project_roles'].queryset = ExORole.objects.filter(code__in=queryset)
        self.fields['teams'].queryset = self.context.get('view').project.teams.all()

    def update(self, instance, validated_data):
        exo_roles = validated_data.pop('project_roles', [])
        project = self.context.get('view').project
        project_roles = ProjectRole.objects.filter(
            project=project, exo_role__in=exo_roles)
        teams = validated_data.pop('teams', [])
        UserProjectRole.objects.update_user_in_project(
            user_from=validated_data.get('created_by'),
            user=instance,
            project=self.context.get('view').project,
            project_roles=project_roles,
            teams=teams,
        )
        if not project.is_draft:
            RolesChangedTask().s(
                project_id=project.id,
                user_id=instance.id).apply_async()
        return instance


class ParticipantUpdateSerializer(serializers.ModelSerializer):
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
        model = get_user_model()
        fields = ['name', 'email', 'teams', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teams'].queryset = self.context.get('view').project.teams.all()

    def update(self, instance, validated_data):
        teams = validated_data.pop('teams', [])
        UserProjectRole.objects.update_participant_in_project(
            user_from=validated_data.get('created_by'),
            user=instance,
            project=self.context.get('view').project,
            name=validated_data.get('name'),
            email=validated_data.get('email'),
            teams=teams,
        )
        return instance


class ParticipantTeamsUpdateSerializer(serializers.ModelSerializer):
    teams = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        many=True,
        required=False)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = get_user_model()
        fields = ['teams', 'created_by']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teams'].queryset = self.context.get('view').project.teams.all()

    def update(self, instance, validated_data):
        teams = validated_data.pop('teams', [])
        UserProjectRole.objects.update_teams_in_project(
            user_from=validated_data.get('created_by'),
            user=instance,
            project=self.context.get('view').project,
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
            teams=teams,
        )
        return instance
