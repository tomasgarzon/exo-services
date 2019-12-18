from django.shortcuts import get_object_or_404
from rest_framework import serializers

from files.api.serializers.mixins import FilesCreationSerializerMixin
from forum.models import Post

from .attachment import ForumAttachmentSerializer
from .author import ForumAuthorSerializer
from .mixins import ForumCommonMixin
from ...models import Answer


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = '__all__'


class AnswerPostSerializer(
        ForumCommonMixin,
        serializers.ModelSerializer):
    can_edit = serializers.SerializerMethodField()
    can_vote = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    your_rating = serializers.SerializerMethodField()
    counter_rating = serializers.SerializerMethodField()
    seen = serializers.SerializerMethodField()
    uploaded_files = ForumAttachmentSerializer(many=True)
    created_by = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    num_likes = serializers.SerializerMethodField()
    thread_pk = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'pk',
            'avg_rating',
            'can_edit',
            'can_vote',
            'created',
            'created_by',
            'created_by_role',
            'comment',
            'counter_rating',
            'liked',
            'modified',
            'num_likes',
            'uploaded_files',
            'seen',
            'thread_pk',
            'your_rating',
        ]

    def get_thread_pk(self, instance):
        return instance.post.pk

    def get_can_vote(self, obj):
        return obj.can_rate(
            self.context['request'].user,
            raise_exceptions=False)

    def get_can_edit(self, obj):
        return obj.can_edit(
            self.context['request'].user,
            raise_exception=False)

    def get_seen(self, obj):
        return obj.has_seen(
            self.context['request'].user)

    def get_created_by(self, obj):
        self.context['project'] = obj.post.project or None
        serializer = ForumAuthorSerializer(obj.created_by, context=self.context)
        return serializer.data


class AnswerCreateUpdateSerializer(
        FilesCreationSerializerMixin,
        serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['comment', 'id']

    def create(self, validated_data):
        post_id = self.context['view'].kwargs.get('pk')
        user_from = validated_data.get('user_from')
        post = get_object_or_404(Post, pk=post_id)
        answer = post.reply(user_from, validated_data.get('comment'))
        self.save_files(user_from=user_from, instance=answer)
        return answer

    def update(self, instance, validated_data):
        user_from = validated_data.get('user_from')
        response = super().update(instance, validated_data)
        instance.action_update(user_from)
        self.save_files(user_from=user_from, instance=instance, delete_old=True)
        return response

    def to_representation(self, obj):
        return AnswerPostSerializer(
            obj, context={'request': self.context.get('request')}
        ).data


class AnswerPostSwarmSerializer(AnswerPostSerializer):
    swarm_pk = serializers.SerializerMethodField()
    swarm_team_pk = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'pk',
            'avg_rating',
            'can_edit',
            'can_vote',
            'created',
            'created_by',
            'created_by_role',
            'comment',
            'counter_rating',
            'liked',
            'modified',
            'num_likes',
            'uploaded_files',
            'seen',
            'swarm_pk',
            'swarm_team_pk',
            'thread_pk',
            'your_rating',
        ]

    def get_swarm_pk(self, instance):
        return instance.post.qa_session.pk

    def get_swarm_team_pk(self, instance):
        return instance.post.content_object.pk
