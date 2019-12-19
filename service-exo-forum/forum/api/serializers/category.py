from rest_framework import serializers

from keywords.api.serializers.keyword import KeywordSerializer

from .post import PostListSerializer
from ...models import Category


class CategoryNoQuestionsSerializer(serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()
    can_leave = serializers.SerializerMethodField()
    can_post = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    user_status = serializers.SerializerMethodField()

    class Meta:
        model = Category
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
        ]

    def get_tags(self, instance):
        return KeywordSerializer(instance.tags.all(), many=True).data

    def get_can_post(self, instance):
        return instance.can_post(
            self.context['request'].user)

    def get_can_edit(self, instance):
        return instance.can_edit(
            self.context['request'].user)

    def get_can_leave(self, instance):
        return instance.can_leave(self.context['request'].user)

    def get_user_status(self, instance):
        return instance.user_status(self.context['request'].user)


class CategorySerializer(CategoryNoQuestionsSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Category
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
            'user_status',
        ]

    def get_questions(self, instance):
        return PostListSerializer(
            instance.posts.all(),
            many=True,
            context=self.context
        ).data
