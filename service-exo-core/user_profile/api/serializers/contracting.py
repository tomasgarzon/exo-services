from rest_framework import serializers

from consultant.models import ContractingData


class ContractingDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContractingData
        exclude = ('profile', )
