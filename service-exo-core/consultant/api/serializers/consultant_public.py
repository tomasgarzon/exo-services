from rest_framework import serializers

from consultant.api.serializers.consultant_profile import ConsultantExOProfileSerializer
from core.api.serializers.language import LanguageSerializer
from exo_area.api.serializers.exo_area import ConsultantExOAreaSerializer
from exo_attributes.api.serializers.exo_attribute import ExOConsultantAttributeSerializer
from exo_certification.api.serializers.certification_role import CertificationRoleSerializer
from relation.api.serializers.consultant.industry import ConsultantIndustrySerializer
from relation.api.serializers.consultant.keyword import ConsultantKeywordSerializer

from ...models import Consultant


class ConsultantPublicSerializer(serializers.ModelSerializer):
    exo_areas = ConsultantExOAreaSerializer(many=True)
    exo_attributes = ExOConsultantAttributeSerializer(many=True)
    exo_profile = ConsultantExOProfileSerializer(instance='exo_profile')
    industries = ConsultantIndustrySerializer(many=True)
    languages = LanguageSerializer(many=True)
    keywords = ConsultantKeywordSerializer(many=True)
    certifications = serializers.SerializerMethodField()

    class Meta:
        model = Consultant
        fields = [
            'pk',
            'exo_areas',
            'exo_attributes',
            'exo_profile',
            'industries',
            'keywords',
            'languages',
            'certifications',
        ]

    def get_certifications(self, obj):
        return CertificationRoleSerializer(
            obj.certification_roles.all(),
            many=True,
            context={'user': obj.user}
        ).data
