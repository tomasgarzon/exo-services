from rest_framework import serializers

from exo_role.models import CertificationRole

from ....models import ConsultantRole


class ConsultantRoleSerializer(serializers.ModelSerializer):

    certification_role = serializers.PrimaryKeyRelatedField(queryset=CertificationRole.objects.all())

    class Meta:
        model = ConsultantRole
        fields = ['id', 'certification_role', 'created_by', 'consultant']
