from rest_framework import serializers

from keywords.models import Keyword

from ....models import ConsultantKeyword


class TagSerializer(serializers.Serializer):
    name = serializers.CharField()


class KeywordSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)

    class Meta:
        model = Keyword
        fields = ['name', 'tags']
        ref_name = 'KeywordSerializerConsultant'


class ConsultantKeywordSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer()

    class Meta:
        model = ConsultantKeyword
        fields = ['level', 'keyword']
