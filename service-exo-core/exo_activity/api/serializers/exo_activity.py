from rest_framework import serializers

from ...models import ExOActivity


class ExOActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = ExOActivity
        fields = [
            'code',
            'description',
            'name',
            'pk',
        ]
