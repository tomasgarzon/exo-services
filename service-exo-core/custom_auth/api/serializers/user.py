from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.conf import settings

from rest_framework import serializers

from agreement.api.serializers.agreement import UserAgreementSerializer
from achievement.api.serializers.user_achievement import UserAchievementSerializer
from exo_certification.api.serializers.certification_request import CertificationRequestSerializer
from exo_certification.api.serializers.certification_role import CertificationRoleSerializer
from exo_hub.api.serializers.hub import ExOHubSerializer
from utils.drf.serializers import TimezoneField

from ...jwt_helpers import _build_jwt
from ...helpers import UserProfileWrapper
from .certification_request_helper import construct_exo_certification_request


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ['name']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['name']
        ref_name = 'GroupSerializerUser'


class UserSerializer(serializers.ModelSerializer):
    user_agreements = UserAgreementSerializer(many=True, source='agreements')
    user_position = serializers.CharField()
    segment = serializers.CharField()
    profile_picture = serializers.SerializerMethodField()
    user_permissions = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    consultant_id = serializers.IntegerField(source='consultant.pk')
    platform_language = serializers.SerializerMethodField()
    entry_point = serializers.SerializerMethodField()
    groups = GroupSerializer(many=True)
    timezone = TimezoneField(required=False, allow_null=True)
    achievements = UserAchievementSerializer(many=True)
    hubs = ExOHubSerializer(many=True, source='_hubs')
    intercom_hash = serializers.CharField()
    profile_url = serializers.SerializerMethodField()
    is_openexo_member = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    certification_requests = serializers.SerializerMethodField()
    desired_activities = serializers.SerializerMethodField()
    sections_visited = serializers.ListField(source='get_sections_visited')

    class Meta:
        model = get_user_model()
        exclude = [
            'password',
            'date_joined',
            '_username',
        ]

    def get_agreements(self, obj):
        pass

    def get_profile_picture(self, obj):
        images = []
        for width, height in obj._meta.get_field('profile_picture').thumbnails:
            value = (
                (width, height),
                obj.profile_picture.get_thumbnail_url(width, height),
            )
            images.append(value)
        return images

    def get_platform_language(self, obj):
        return obj.platform_language

    def get_token(self, obj):
        return _build_jwt(obj)

    def get_projects(self, obj):
        data = {'consultant': 0, 'participant': 0, 'total': 0}
        if obj.is_consultant:
            data['consultant'] = obj.consultant.roles.filter_by_user(obj).projects().distinct().count()
        data['participant'] = obj.projects_member.filter_by_user(obj).projects().distinct().count()
        data['total'] = data['participant'] + data['consultant']
        return data

    def get_status(self, obj):
        if obj.is_consultant:
            return obj.consultant.status
        else:
            return settings.CONSULTANT_STATUS_CH_ACTIVE if obj.is_active else settings.CONSULTANT_STATUS_CH_DISABLED

    def get_user_permissions(self, obj):
        return obj.user_permissions.values_list('codename', flat=True)

    def get_profile_url(self, obj):
        user_wrapper = UserProfileWrapper(obj)
        return user_wrapper.profile_public_slug_url

    def get_is_openexo_member(self, obj):
        user_wrapper = UserProfileWrapper(obj)
        return user_wrapper.is_openexo_member

    def get_certification_requests(self, obj):
        # TODO: After fix CertificationRequest for ExO Foundation rewrite this
        certification_requests = []
        if obj.is_consultant:
            exo_foundation_certification_request = construct_exo_certification_request(obj)
            user_certifications = list(obj.certification_request.all())
            if exo_foundation_certification_request:
                user_certifications.append(exo_foundation_certification_request)

            certification_requests = CertificationRequestSerializer(
                user_certifications,
                many=True
            ).data

        return certification_requests

    def get_certifications(self, obj):
        certifications = []

        if obj.is_consultant:
            certifications = CertificationRoleSerializer(
                obj.consultant.certification_roles.all(),
                many=True,
                context={'user': obj}
            ).data

        return certifications

    def get_desired_activities(self, obj):
        activities_names = []
        if obj.is_consultant:
            try:
                activities = obj.consultant.exo_profile.exo_activities.filter(
                    status=settings.RELATION_ACTIVITY_STATUS_CH_ACTIVE,
                )
            except Exception:
                activities = []
            activities_names = [_.exo_activity.name for _ in activities]

        return activities_names

    def get_entry_point(self, obj):
        entry_point = None
        if hasattr(obj, 'registration_process'):
            entry_point = obj.registration_process.real_entry_point

        return entry_point


class UserUUIDSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    consultant_id = serializers.IntegerField(source='consultant.pk')
    groups = GroupSerializer(many=True)
    profile_url = serializers.SerializerMethodField()
    linkedin = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'uuid', 'short_name', 'full_name', 'email',
            'groups', 'profile_picture', 'consultant_id',
            'user_title', 'profile_url', 'bio_me',
            'linkedin', 'certifications',
            'is_staff', 'is_superuser', 'is_active',
            'slug']

    def get_profile_url(self, obj):
        user_wrapper = UserProfileWrapper(obj)
        return user_wrapper.profile_public_slug_url

    def get_profile_picture(self, obj):
        images = []
        for width, height in obj._meta.get_field('profile_picture').thumbnails:
            value = (
                (width, height),
                obj.profile_picture.get_thumbnail_url(width, height),
            )
            images.append(value)
        return images

    def get_linkedin(self, obj):
        obj.initialize_social_networks()
        return obj.linkedin.value

    def get_certifications(self, obj):
        certifications = []
        if obj.is_consultant:
            certifications = CertificationRoleSerializer(
                obj.consultant.certification_roles.all(),
                many=True,
                context={'user': obj}
            ).data
        return certifications


class UserSimpleSerializer(serializers.ModelSerializer):
    profile_pictures = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'pk',
            'full_name',
            'user_title',
            'profile_pictures',
            'slug',
        ]

    def get_profile_pictures(self, obj):
        images = []
        for width, height in obj._meta.get_field('profile_picture').thumbnails:
            value = (
                (width, height),
                obj.profile_picture.get_thumbnail_url(width, height),
            )
            images.append(value)
        return images
