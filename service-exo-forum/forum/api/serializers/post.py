from django.conf import settings
from rest_framework import serializers, exceptions
from rest_framework.exceptions import PermissionDenied

from circles.models import Circle
from files.api.serializers.mixins import FilesCreationSerializerMixin
from keywords.api.serializers.keyword import KeywordSerializer
from keywords.api.serializers.keyword_mixin import KeywordSerializerMixin

from .attachment import ForumAttachmentSerializer
from .mixins import ForumCommonMixin
from .author import ForumAuthorSerializer
from ...models import Post


class PostListSerializer(
        ForumCommonMixin,
        serializers.ModelSerializer):
    seen = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    answers_unseen = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    your_rating = serializers.SerializerMethodField()
    counter_rating = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    num_likes = serializers.SerializerMethodField()
    num_views = serializers.IntegerField(source='count_views')

    class Meta:
        model = Post
        fields = [
            'pk',
            'answers',
            'answers_unseen',
            'avg_rating',
            'can_edit',
            'counter_rating',
            'created',
            'created_by',
            'description',
            'liked',
            'modified',
            'num_likes',
            'num_views',
            'title',
            'seen',
            'slug',
            'your_rating',
            'has_been_edited',
        ]

    def get_answers(self, obj):
        return obj.answers.count()

    def get_can_edit(self, obj):
        return obj.can_update_or_remove(
            self.context['request'].user,
            raise_exceptions=False)

    def get_new_answers(self, obj):
        user = self.context['request'].user
        return obj.new_answers(user)

    def get_answers_unseen(self, obj):
        user = self.context['request'].user
        return obj.answers_unseen(user)

    def get_created_by(self, obj):
        self.context['project'] = obj.project or None
        serializer = ForumAuthorSerializer(obj.created_by, context=self.context)
        return serializer.data


class PostDetailSerializer(
        PostListSerializer):
    can_reply = serializers.SerializerMethodField()
    uploaded_files = ForumAttachmentSerializer(many=True)
    tags = KeywordSerializer(many=True)

    class Meta:
        model = Post
        fields = [
            'pk',
            'answers',
            'answers_unseen',
            'avg_rating',
            'can_edit',
            'can_reply',
            'counter_rating',
            'created',
            'created_by',
            'description',
            'liked',
            'modified',
            'num_likes',
            'num_views',
            'slug',
            'seen',
            'tags',
            'title',
            'uploaded_files',
            'url',
            'your_rating',
            'has_been_edited',
        ]

    def get_can_reply(self, instance):
        return instance.can_reply(
            self.context.get('request').user, False)


class PostDetailSwarmSerializer(PostDetailSerializer):
    swarm_pk = serializers.SerializerMethodField()
    swarm_team_pk = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'pk',
            'answers',
            'answers_unseen',
            'avg_rating',
            'can_edit',
            'can_reply',
            'counter_rating',
            'created',
            'created_by',
            'description',
            'liked',
            'modified',
            'num_likes',
            'num_views',
            'slug',
            'seen',
            'swarm_pk',
            'swarm_team_pk',
            'tags',
            'title',
            'uploaded_files',
            'url',
            'your_rating',
            'has_been_edited',
        ]

    def get_swarm_pk(self, instance):
        return instance.qa_session.pk

    def get_swarm_team_pk(self, instance):
        return instance.content_object.pk


class PostCreateSerializer(
        KeywordSerializerMixin,
        FilesCreationSerializerMixin,
        serializers.ModelSerializer):
    tags = KeywordSerializer(many=True, required=False)
    circle = serializers.PrimaryKeyRelatedField(
        queryset=Circle.objects.all(),
        required=False)
    url = serializers.CharField(required=False)

    class Meta:
        model = Post
        fields = [
            'title',
            'description',
            'tags',
            'circle',
            'pk',
            'slug',
            'url'
        ]
        read_only_fields = ['slug', 'url']

    def validate(self, attrs):
        if 'circle' not in attrs and not self.context['request'].user.is_staff:
            raise PermissionDenied
        return super().validate(attrs)

    def validate_circle(self, value):
        value.check_user_can_post(self.context.get('request').user)
        return value

    def create(self, validated_data):
        user_from = self.context['request'].user
        tags = self.sync_tags(
            tags=validated_data.get('tags', []),
            user=user_from)

        _type = settings.FORUM_CH_ANNOUNCEMENT
        if validated_data.get('circle', None):
            _type = settings.FORUM_CH_CIRCLE

        post_for_type = self.Meta.model(_type=_type)
        data_for_creating_post = {
            'user_from': user_from,
            'title': validated_data.get('title'),
            'description': validated_data.get('description'),
            'tags': tags,
        }
        post = None
        try:

            if post_for_type.is_circle:
                post = self.Meta.model.objects.create_circle_post(
                    circle=validated_data.get('circle'),
                    **data_for_creating_post
                )
            elif post_for_type.is_announcement:
                post = self.Meta.model.objects.create_announcement_post(
                    **data_for_creating_post)
        except Exception:
            raise exceptions.PermissionDenied

        # Create files
        self.save_files(user_from=user_from, instance=post)
        return post

    def to_representation(self, obj):
        context = {'request': self.context.get('request')}
        return PostDetailSerializer(obj, context=context).data


class PostUpdateSerializer(
        KeywordSerializerMixin,
        FilesCreationSerializerMixin,
        serializers.ModelSerializer):
    tags = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = [
            'description',
            'pk',
            'tags',
            'title',
        ]

    def validate(self, data):
        user = self.context.get('request').user
        self.instance.can_update_or_remove(user)
        return data

    def update(self, instance, validated_data):
        user_from = self.context.get('request').user
        tags = self.sync_tags(
            tags=validated_data.get('tags', []),
            user=user_from,
        )
        validated_data['tags'] = tags
        Post.objects.update_post(
            post=instance, **validated_data)
        # Files
        self.save_files(
            user_from=user_from,
            instance=instance,
            delete_old=True)
        return instance

    def to_representation(self, obj):
        context = {'request': self.context.get('request')}
        return PostDetailSerializer(obj, context=context).data
