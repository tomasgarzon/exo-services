from rest_framework import serializers

from relation.models import ConsultantExOAttribute
from consultant.models import Consultant


class ConsultantExOAttributeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultantExOAttribute
        fields = ['id', 'level']
        extra_kwargs = {'id': {'read_only': False}}


class ConsultantExOAttributesSerializer(serializers.ModelSerializer):
    exo_attributes = ConsultantExOAttributeSerializer(
        many=True,
    )

    class Meta:
        model = Consultant
        fields = ['exo_attributes']

    def update(self, instance, validated_data):
        for value in validated_data.get('exo_attributes'):
            exo_attribute = instance.exo_attributes.get(pk=value['id'])
            serializer = ConsultantExOAttributeSerializer(
                data=value,
                instance=exo_attribute,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return instance
