from rest_framework import serializers

from ..models import Industry


class IndustrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = ['id', 'name']


class IndustrySimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = ['name']


class IndustrySelect2Serializer(serializers.ModelSerializer):

    class Meta:
        model = Industry
        fields = ['id', 'text']

    text = serializers.CharField(required=True, source='name')
