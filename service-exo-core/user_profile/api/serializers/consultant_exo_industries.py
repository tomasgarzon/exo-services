from django.conf import settings

from rest_framework import serializers

from consultant.models import Consultant
from industry.models import Industry


class IndustrySerializer(serializers.Serializer):

    name = serializers.CharField(source='industry.name')
    level = serializers.ChoiceField(choices=settings.RELATION_INDUSTRIES_CHOICES)

    class Meta:
        fields = ['name', 'level']
        ref_name = 'IndustryProfileSerializer'


class ConsultantIndustrySerializer(serializers.ModelSerializer):
    industries = IndustrySerializer(
        many=True,
    )

    class Meta:
        model = Consultant
        fields = ['industries']
        ref_name = 'ConsultantIndustriesSerializer'

    def update(self, instance, validated_data):
        industries = Industry.objects.update_industries(
            user_from=self.context.get('request').user,
            industries_name=[value.get('industry').get('name') for value in validated_data.get('industries', [])],
        )
        instance.industries.update_from_values(
            consultant=instance,
            industries=industries,
            industries_level=validated_data.get('industries'),
        )
        return instance
