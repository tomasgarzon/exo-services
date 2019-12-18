from rest_framework import serializers
from django.conf import settings

CH_CURRENCY = settings.OPPORTUNITIES_CH_CURRENCY + settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY


class BudgetSerializer(serializers.Serializer):
    budget = serializers.CharField()
    currency = serializers.ChoiceField(
        choices=CH_CURRENCY)
