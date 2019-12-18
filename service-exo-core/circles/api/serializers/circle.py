from rest_framework import serializers

from exo_role.api.serializers import CertificationRoleSerializer
from forum.api.serializers.post import PostListSerializer
from keywords.api.serializers.keyword import KeywordSerializer

from ...helpers import (
    get_circle_total_members,
    get_circle_last_questions,
    get_circle_post_permissions,
    get_circle_user_status,
    get_circle_tags,
    get_circle_edit_permissions,
    get_circle_leave_permissions
)
from ...models import Circle


class CircleNoQuestionsSerializer(serializers.ModelSerializer):
    total_members = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_leave = serializers.SerializerMethodField()
    can_post = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()
    certification_required = CertificationRoleSerializer()

    class Meta:
        model = Circle
        fields = [
            'can_edit',
            'can_leave',
            'can_post',
            'description',
            'name',
            'image',
            'slug',
            'tags',
            'total_members',
            'type',
            'user_status',
            'certification_required'
        ]

    def get_tags(self, instance):
        tags = get_circle_tags(instance)
        return KeywordSerializer(tags, many=True).data

    def get_total_members(self, instance):
        return get_circle_total_members(instance)

    def get_can_post(self, instance):
        return get_circle_post_permissions(
            instance, self.context['request'].user)

    def get_can_edit(self, instance):
        return get_circle_edit_permissions(
            instance, self.context['request'].user)

    def get_can_leave(self, instance):
        return get_circle_leave_permissions(
            instance, self.context['request'].user)

    def get_user_status(self, instance):
        return get_circle_user_status(
            instance, self.context['request'].user)


class CircleSerializer(CircleNoQuestionsSerializer):
    questions = serializers.SerializerMethodField()
    certification_required = CertificationRoleSerializer()

    class Meta:
        model = Circle
        fields = [
            'can_edit',
            'can_leave',
            'can_post',
            'description',
            'name',
            'image',
            'questions',
            'slug',
            'tags',
            'total_members',
            'type',
            'user_status',
            'certification_required'
        ]

    def get_questions(self, instance):
        return PostListSerializer(
            get_circle_last_questions(instance),
            many=True,
            context=self.context
        ).data
