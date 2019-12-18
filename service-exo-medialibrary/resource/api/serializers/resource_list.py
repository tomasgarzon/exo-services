from rest_framework import serializers

from ...models import Resource
from .tag import TagSimpleSerializer


class ResourceListSerializer(serializers.ModelSerializer):
    iframe = serializers.SerializerMethodField()
    tags = TagSimpleSerializer(many=True)

    class Meta:
        model = Resource
        fields = [
            'pk',
            'name',
            'description',
            'tags',
            'sections',
            'projects',
            'status',
            'link',
            'duration',
            'iframe',
            'thumbnail',
            'created',
            'modified',
            'internal',
        ]

    def get_iframe(self, obj):
        return obj.get_video_iframe()
