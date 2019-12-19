from rest_framework import serializers

from files.api.serializers import UploadedFileSerializer
from keywords.api.serializers.keyword import KeywordSerializer
from keywords.api.serializers.keyword_mixin import KeywordSerializerMixin

from .category import CategoryNoQuestionsSerializer
from ...models import Category


class CategoryCreateSerializer(
        KeywordSerializerMixin,
        serializers.ModelSerializer):
    image = UploadedFileSerializer(required=False, read_only=True)
    tags = KeywordSerializer(many=True, required=False)

    class Meta:
        model = Category
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
        category_data = {
            'name': validated_data.get('name'),
            'description': validated_data.get('description'),
            'created_by': user_from,
        }
        image = self.context['request'].data.get('image', None)
        if image:
            category_data['image'] = image.get('url', None)
        category = Category.objects.create(**category_data)
        category.tags.add(*tags)
        category.add_user(user_from)
        return category

    def update(self, instance, validated_data):
        user_from = self.context['request'].user
        instance.can_edit(user_from)
        validated_data['tags'] = self.sync_tags(
            tags=validated_data.get('tags', []),
            user=user_from)
        image = self.context['request'].data.get('image', None)
        if image:
            validated_data['image'] = image.get('url', None)
        return Category.objects.update_category(
            instance, **validated_data)

    def to_representation(self, instance):
        return CategoryNoQuestionsSerializer(
            instance, context=self.context).data
