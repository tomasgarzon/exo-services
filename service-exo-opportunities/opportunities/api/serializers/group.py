from rest_framework import serializers

from django.contrib.auth import get_user_model

from exo_role.models import ExORole, CertificationRole

from utils.drf.relations import UserUUIDRelatedField

from ...models import OpportunityGroup


class OpportunityGroupSerializer(serializers.ModelSerializer):

    managers = UserUUIDRelatedField(
        many=True, slug_field='uuid',
        queryset=get_user_model().objects.all())
    exo_role = serializers.SlugRelatedField(
        slug_field='code',
        queryset=ExORole.objects.all(),
        required=True)
    certification_required = serializers.SlugRelatedField(
        slug_field='code',
        queryset=CertificationRole.objects.all(),
        required=True)
    consumed = serializers.SerializerMethodField()

    class Meta:
        model = OpportunityGroup
        read_only_fields = ['uuid']
        fields = [
            'uuid', 'related_uuid', 'total', 'pk',
            'exo_role', 'certification_required', 'managers',
            'entity', 'duration_value', 'duration_unity',
            'budgets', 'consumed', 'origin']

    def get_consumed(self, obj):
        obj.refresh_from_db()
        return obj.consumed
