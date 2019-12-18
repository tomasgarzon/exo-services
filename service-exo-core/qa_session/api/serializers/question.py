from rest_framework import serializers

from files.api.serializers.mixins import FilesCreationSerializerMixin
from forum.api.serializers.post import PostDetailSerializer
from forum.models import Post
from keywords.api.serializers.keyword import KeywordSerializer
from keywords.api.serializers.keyword_mixin import KeywordSerializerMixin

from ...models import QASessionTeam


class QAQuestionWriteSerializer(
        FilesCreationSerializerMixin,
        KeywordSerializerMixin,
        serializers.ModelSerializer):
    tags = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = [
            'pk',
            'title',
            'description',
            'tags',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        swarm_id = self.context['view'].kwargs.get('swarm_id', None)
        qa_session_team = QASessionTeam.objects.get(pk=swarm_id)
        validated_data['tags'] = self.sync_tags(
            tags=validated_data.get('tags'),
            user=user)
        post = self.Meta.model.objects.create_project_qa_session_post(
            qa_session_team=qa_session_team, user_from=user, **validated_data)
        self.save_files(user_from=user, instance=post)
        return post

    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['user_from'] = user
        validated_data['tags'] = self.sync_tags(
            tags=validated_data.get('tags'),
            user=user)
        Post.objects.update_post(
            post=instance, **validated_data)
        self.save_files(
            user_from=user,
            instance=instance,
            delete_old=True)
        return instance

    def to_representation(self, instance):
        context = self.context
        serializer = PostDetailSerializer(instance, context=context)
        return serializer.data
