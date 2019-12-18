from rest_framework import serializers

from exo_accounts.models import SocialNetwork


class SocialNetworkSerializer(serializers.ModelSerializer):

    class Meta:
        model = SocialNetwork
        fields = [
            'network_type', 'value'
        ]
