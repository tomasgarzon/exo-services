from rest_framework import serializers
from exo_role.api.serializers import CategoryExORoleSerializer, ExORoleCategorySerializer
from ...models import Job


class JobSerializer(serializers.ModelSerializer):
    category = ExORoleCategorySerializer()
    exo_role = CategoryExORoleSerializer()

    class Meta:
        model = Job
        fields = [
            'pk',
            'uuid',
            'category',
            'title',
            'start', 'end',
            'status',
            'status_detail',
            'exo_role',
            'url',
            'extra_data',
        ]
