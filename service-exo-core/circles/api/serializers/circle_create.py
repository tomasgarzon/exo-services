from rest_framework import serializers

from files.api.serializers import UploadedFileSerializer
from keywords.api.serializers.keyword import KeywordSerializer
from keywords.api.serializers.keyword_mixin import KeywordSerializerMixin

from .circle import CircleNoQuestionsSerializer
from ...models import Circle


class CircleCreateSerializer(
        KeywordSerializerMixin,
        serializers.ModelSerializer):
    image = UploadedFileSerializer(required=False, read_only=True)
    tags = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Circle
        fields = [
            'name',
            'description',
            'image',
            'tags',
        ]

    def create(self, validated_data):
        user_from = self.context['request'].user
        tags = self.sync_tags(
            tags=validated_data.get('tags', []),
            user=user_from)
        circle_data = {
            'name': validated_data.get('name'),
            'description': validated_data.get('description'),
            'created_by': user_from,
        }
        image = self.context['request'].data.get('image', None)
        if image:
            circle_data['image'] = image.get('url', None)
        circle = Circle.objects.create(**circle_data)
        circle.tags.add(*tags)
        circle.add_user(user_from)
        return circle

    def update(self, instance, validated_data):
        user_from = self.context['request'].user
        instance.can_edit(user_from)
        validated_data['tags'] = self.sync_tags(
            tags=validated_data.get('tags', []),
            user=user_from)
        image = self.context['request'].data.get('image', None)
        if image:
            validated_data['image'] = image.get('url', None)
        return Circle.objects.update_circle(
            instance, **validated_data)

    def to_representation(self, instance):
        return CircleNoQuestionsSerializer(
            instance, context=self.context).data
