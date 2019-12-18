from rest_framework import serializers

from ...models import Resource, Tag
from ...conf import settings
from .resource_list import ResourceListSerializer


class ResourceUpdateSerializer(serializers.ModelSerializer):
    url = serializers.URLField(
        read_only=True)
    name = serializers.CharField(
        required=True,
        max_length=50)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        allow_empty=False)
    sections = serializers.MultipleChoiceField(
        choices=settings.RESOURCE_CH_SECTIONS,
        required=False)

    class Meta:
        model = Resource
        fields = [
            'url',
            'name',
            'description',
            'tags',
            'sections',
        ]

    def to_representation(self, obj):
        return ResourceListSerializer(obj).data
