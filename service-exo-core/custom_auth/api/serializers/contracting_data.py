from django.contrib.auth import get_user_model
from rest_framework import serializers

from consultant.models import ContractingData


class ContractingDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContractingData
        fields = [
            'name',
            'tax_id',
            'address',
            'company_name',
        ]


class UserPaymentDataSerializer(serializers.ModelSerializer):
    contracting_data = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'full_name',
            'email',
            'contracting_data',
        ]

    def get_contracting_data(self, instance):
        try:
            contracting_data = instance.consultant.exo_profile.contracting_data
        except Exception:
            contracting_data = None
        return ContractingDataSerializer(contracting_data).data
