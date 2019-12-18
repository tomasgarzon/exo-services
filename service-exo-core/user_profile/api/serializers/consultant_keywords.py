from django.conf import settings

from rest_framework import serializers

from consultant.models import Consultant
from keywords.models import Keyword


class KeywordSerializer(serializers.Serializer):

    name = serializers.CharField(source='keyword.name')
    level = serializers.ChoiceField(choices=settings.RELATION_KEYWORD_CHOICES)

    class Meta:
        fields = ['name', 'level']
        ref_name = 'KeywordSerializerSimple'


class ConsultantKeywordSerializer(serializers.ModelSerializer):
    expertise = KeywordSerializer(
        many=True,
        allow_null=True,
        required=False,
    )
    technology = KeywordSerializer(
        many=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Consultant
        fields = ['expertise', 'technology']
        ref_name = 'ConsultantKeywordSerializer'

    def update_keywords(self, instance, values, tag):
        keywords = Keyword.objects.update_keywords(
            user_from=self.context.get('request').user,
            keywords_name=[value.get('keyword').get('name') for value in values],
            tags=[tag],
        )
        instance.keywords.update_from_values(
            consultant=instance,
            keywords=keywords,
            keywords_level=values,
            tag=tag,
        )

    def update(self, instance, validated_data):
        if validated_data.get('expertise', None) is not None:
            self.update_keywords(
                instance,
                validated_data.get('expertise', []),
                tag=settings.KEYWORDS_CH_EXPERTISE,
            )
        if validated_data.get('technology', None) is not None:
            self.update_keywords(
                instance,
                validated_data.get('technology', []),
                tag=settings.KEYWORDS_CH_TECHNOLOGY,
            )
        return instance
