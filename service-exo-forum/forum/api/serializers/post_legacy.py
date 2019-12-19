from rest_framework import serializers

from forum.helpers import get_circle_by_object
from ...models import Post


class PostLegacySerializer(serializers.ModelSerializer):
    circle_slug = serializers.SerializerMethodField()
    is_removed = serializers.SerializerMethodField()
    post_slug = serializers.CharField(source='slug')

    class Meta:
        model = Post
        fields = [
            'pk',
            'circle_slug',
            'is_removed',
            'post_slug',
        ]

    def get_circle_slug(self, instance):
        circle = get_circle_by_object(instance)
        return circle.slug

    def get_is_removed(self, instance):
        return True if instance.is_removed else False
