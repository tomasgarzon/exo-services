from rest_framework import serializers

from ...models import Tag


class TagSerializer(serializers.ModelSerializer):
    category_slug = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['pk', 'name', 'slug', 'category_slug', 'default_show_filter']

    def get_category_slug(self, obj):
        return obj.category.slug if obj.category else None


class TagSimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['pk', 'name']
