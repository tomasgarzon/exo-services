from django.conf import settings

from rest_framework import serializers

from exo_role.api.serializers import ExORoleSerializer

from team.models.team import Team
from project.api.serializers.project import ProjectSerializer

from ....models import ConsultantProjectRole, UserProjectRole


class ConsultantProjectRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultantProjectRole
        fields = ['consultant', 'project', 'exo_role', 'status']


class ConsultantProjectRoleFullSerializer(serializers.ModelSerializer):

    full_name = serializers.CharField(
        read_only=True,
        source='consultant.user.get_full_name',
    )
    email = serializers.EmailField(source='consultant.user.email')
    pk_consultant = serializers.IntegerField(source='consultant.id')
    team = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    url_profile = serializers.SerializerMethodField()

    class Meta:
        model = ConsultantProjectRole
        fields = [
            'pk',
            'full_name', 'email',
            'exo_role',
            'team', 'pk_consultant',
            'thumbnail', 'url_profile',
        ]

    def get_team(self, obj):
        try:
            return Team.objects.filter_by_project(
                obj.project,
            ).filter_by_coach(obj.consultant)[0].name
        except IndexError:
            return None

    def get_thumbnail(self, obj):
        return obj.consultant.user.profile_picture.get_thumbnail_url(
            settings.EXO_ACCOUNTS_MEDIUM_IMAGE_SIZE,
            settings.EXO_ACCOUNTS_MEDIUM_IMAGE_SIZE,
        )

    def get_url_profile(self, obj):
        return obj.consultant.get_public_profile_v2()


class ConsultantProfileProjectRoleSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    exo_role = ExORoleSerializer()

    class Meta:
        model = ConsultantProjectRole
        fields = [
            'project',
            'exo_role',
            'status',
            'rating'
        ]

    def rating(self, obj):
        return obj.rating or 0


class UserProfileProjectRoleSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    exo_role = ExORoleSerializer()

    class Meta:
        model = UserProjectRole
        fields = [
            'project',
            'exo_role',
            'status',
        ]
