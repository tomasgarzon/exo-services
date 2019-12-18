from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import serializers, exceptions

from utils.drf.user import UserSerializer
from auth_uuid.utils.user_wrapper import UserWrapper
from team.api.serializers.stream import StreamSerializer
from team.api.serializers.role import TeamRoleSerializer

from ...models import Project
from .project_role import ProjectRoleSerializer
from .project_settings import ProjectSettingsSerializer


class ProjectBasicInfoSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    start = serializers.DateField()
    name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True)
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    user_actions = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    settings = ProjectSettingsSerializer(required=False)

    class Meta:
        model = Project
        read_only_fields = ['pk', 'uuid']
        fields = [
            'pk', 'name', 'start', 'customer',
            'location', 'place_id', 'uuid',
            'created_by', 'description',
            'user_actions', 'zone', 'settings']

    def validate(self, data):
        if self.instance:
            user_from = self.context.get('view').request.user
            if self.instance.created_by != user_from and not user_from.is_superuser:
                raise exceptions.ValidationError('Operation not allowed')
        return data

    def get_user_actions(self, obj):
        return obj.user_actions(self.context.get('request').user)

    def get_zone(self, obj):
        return obj.get_zone(self.context.get('request').user)

    def create(self, validated_data):
        return Project.objects.create_project(**validated_data)

    def update(self, instance, validated_data):
        return Project.objects.update_project(instance, **validated_data)


class ProjectListSerializer(ProjectBasicInfoSerializer):

    current_step = serializers.SerializerMethodField()
    project_roles = ProjectRoleSerializer(many=True)
    team_roles = TeamRoleSerializer(many=True)
    users = serializers.SerializerMethodField()
    streams = StreamSerializer(many=True)
    user_actions = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()
    settings = ProjectSettingsSerializer()

    class Meta:
        model = Project
        fields = [
            'pk', 'name', 'start', 'customer',
            'location', 'place_id', 'uuid',
            'streams', 'user_actions',
            'status', 'current_step', 'template_name',
            'project_roles', 'users', 'team_roles',
            'zone', 'description', 'settings']

    def get_current_step(self, obj):
        step = obj.current_step()
        if step is None:
            return {}
        return {'pk': step.pk, 'name': step.name}

    def get_users(self, obj):
        coach_and_head_coach = [
            settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
            settings.EXO_ROLE_CODE_SPRINT_COACH,
        ]
        users = get_user_model().objects.filter(
            user_project_roles__project_role__project=obj,
            user_project_roles__project_role__code__in=coach_and_head_coach,
        ).distinct()
        users_wrapper = [UserWrapper(user=user) for user in users]
        return UserSerializer(users_wrapper, many=True).data

    def get_user_actions(self, obj):
        return obj.user_actions(self.context.get('request').user)

    def get_zone(self, obj):
        return obj.get_zone(self.context.get('request').user)
