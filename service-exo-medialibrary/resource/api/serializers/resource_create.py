from rest_framework import serializers

from embed_video.backends import detect_backend, UnknownBackendException

from .resource_list import ResourceListSerializer
from ...models import Resource, Tag
from ...conf import settings
from ...signals.define import post_save_resource_signal


class ResourceCreateSerializer(serializers.ModelSerializer):
    url = serializers.URLField(
        required=True)
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

    def validate_url(self, data):
        try:
            detect_backend(data)
            if Resource.objects.draft_and_available().filter_by_url(data).exists():
                raise serializers.ValidationError("duplicated")
        except UnknownBackendException:
            raise serializers.ValidationError("invalid")

        return data

    def create(self, validated_data):
        instance = Resource.objects.create(
            status=settings.RESOURCE_CH_STATUS_DRAFT,
            url=validated_data.get("url"),
            name=validated_data.get('name'),
            description=validated_data.get('description'),
            sections=validated_data.get('sections'),
        )
        tags = validated_data.pop("tags")
        instance.tags.set(tags)
        post_save_resource_signal.send(sender=instance)
        instance.upload_video_async(validated_data)
        return instance
