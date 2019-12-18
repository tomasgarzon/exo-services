from rest_framework import serializers

from relation.models import ConsultantExOAttribute

from ...models import ExOAttribute


class ExOAttributeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='_type')

    class Meta:
        model = ExOAttribute
        fields = ['name', 'type']


class ExOConsultantAttributeSerializer(serializers.ModelSerializer):
    exo_attribute = ExOAttributeSerializer()

    class Meta:
        model = ConsultantExOAttribute
        fields = ['pk', 'level', 'exo_attribute']
