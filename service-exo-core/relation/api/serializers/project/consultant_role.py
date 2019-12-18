from rest_framework import serializers

from exo_role.models import ExORole

from consultant.models import Consultant

from ....models import ConsultantProjectRole


class ConsultantProjectRoleSerializer(serializers.ModelSerializer):
    consultant = serializers.PrimaryKeyRelatedField(
        queryset=Consultant.objects.all(),
    )
    exo_role = serializers.PrimaryKeyRelatedField(
        queryset=ExORole.objects.all(),
    )

    class Meta:
        model = ConsultantProjectRole
        fields = ['consultant', 'exo_role', 'pk']
        read_only_fields = ('pk', )

    def get_fields(self):
        fields = super().get_fields()
        fields['exo_role'].queryset = ExORole.objects.all()
        return fields

    def create(self, validated_data):
        project = self._context.get('view').get_project()
        user_from = validated_data.get('user_from')
        project.check_edit_perms(user_from)
        consultant = validated_data.get('consultant')
        exo_role = validated_data.get('exo_role')
        consultant_role, _ = project.get_or_create_consultant(
            user_from, consultant, exo_role,
        )
        return consultant_role
