from rest_framework import serializers

from ...models import Category
from .tag import TagSerializer


class CategorySerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Category
        fields = ['name', 'slug', 'tags']
