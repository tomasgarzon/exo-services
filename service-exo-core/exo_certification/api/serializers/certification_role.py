from rest_framework import serializers

from certification.models import CertificationCredential
from exo_role.models import CertificationRole


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificationCredential
        fields = ['name', 'image', 'accredible_url', 'issued_on', 'pdf']


class CertificationRoleSerializer(serializers.ModelSerializer):
    certificates = serializers.SerializerMethodField()

    class Meta:
        model = CertificationRole
        fields = ['name', 'code', 'description', 'certificates', 'level']

    def get_certificates(self, obj):
        user = self.context.get('user')

        if user:
            consultant_roles = obj.consultants_certified.filter(consultant__user=user)

            if consultant_roles.exists():
                try:
                    credentials = consultant_roles.first().credentials.all()
                    return CredentialSerializer(credentials, many=True).data
                except AttributeError:
                    pass

        return []


class CertificationRoleWithOrderSerializer(serializers.ModelSerializer):
    level = serializers.SerializerMethodField()
    order = serializers.IntegerField()

    class Meta:
        model = CertificationRole
        fields = ['name', 'code', 'description', 'level', 'order']

    def get_level(self, obj):
        return obj.certifications.all().first().level
