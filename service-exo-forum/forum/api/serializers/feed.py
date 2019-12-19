from rest_framework import serializers

from circles.api.serializers.circle import CircleNoQuestionsSerializer

from .post import PostDetailSerializer
from ...helpers import get_circle_by_object
from ...models import Post


class PostFeedSerializer(
        PostDetailSerializer,
        serializers.ModelSerializer):
    circle = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'pk',
            'answers',
            'answers_unseen',
            'avg_rating',
            'can_edit',
            'circle',
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
            'has_been_edited'
        ]

    def get_circle(self, instance):
        circle = get_circle_by_object(instance)
        return CircleNoQuestionsSerializer(
            circle, context=self.context).data
