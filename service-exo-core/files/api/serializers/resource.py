from rest_framework import serializers

from django.contrib.contenttypes.models import ContentType

from team.models import Team

from ...models import Resource


class ResourceSerializer(serializers.ModelSerializer):

    is_link = serializers.BooleanField()
    is_file = serializers.BooleanField()
    url = serializers.URLField()
    type = serializers.CharField()
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Resource
        fields = [
            'name', 'description', 'link',
            'is_link', 'is_file', 'url', 'type',
            'tags', 'id', 'extension',
        ]


class ResourceAPISerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    extension = serializers.CharField(required=False, allow_blank=True)
    mimetype = serializers.CharField(required=False, allow_blank=True)
    _filename = serializers.CharField(required=False, allow_blank=True)
    file_size = serializers.CharField(required=False, allow_blank=True)
    link = serializers.URLField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        new_file = Resource.objects.create_resource(
            user_from=validated_data.get('user_from'),
            root_name=validated_data.get('_filename'),
            name=validated_data.get('name'),
            extension=validated_data.get('extension'),
            content_type=validated_data.get('mimetype'),
            description=validated_data.get('description'),
            link=validated_data.get('link'),
            file_size=validated_data.get('file_size'),
        )
        return new_file


class ResourceRelatedSerializer(serializers.Serializer):
    content_type = serializers.PrimaryKeyRelatedField(queryset=ContentType.objects.all())
    object_id = serializers.IntegerField()
    team = serializers.PrimaryKeyRelatedField(queryset=Team.objects.all())
