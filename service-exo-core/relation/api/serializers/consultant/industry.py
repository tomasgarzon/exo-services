from rest_framework import serializers

from industry.api.serializers import IndustrySimpleSerializer

from ....models import ConsultantIndustry


class ConsultantIndustrySerializer(serializers.ModelSerializer):
    industry = IndustrySimpleSerializer()

    class Meta:
        model = ConsultantIndustry
        fields = ['level', 'industry']
