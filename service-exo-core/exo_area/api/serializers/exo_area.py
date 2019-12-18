from rest_framework import serializers

from relation.models import ConsultantExOArea

from ...models import ExOArea


class ExOAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExOArea
        fields = ['code']


class ConsultantExOAreaSerializer(serializers.ModelSerializer):
    exo_area = ExOAreaSerializer()

    class Meta:
        model = ConsultantExOArea
        fields = ['exo_area']
