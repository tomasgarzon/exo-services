from rest_framework import serializers

from ...models import ExOHub


class ExOHubSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='_type')

    class Meta:
        model = ExOHub
        fields = ('name', 'code')
