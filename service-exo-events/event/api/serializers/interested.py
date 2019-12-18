from django.conf import settings

from rest_framework import serializers

from ...models import Interested, Event


class InterestedListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interested
        fields = ['name', 'email']


class InterestedCreateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.filter_by_category(settings.EXO_ROLE_CATEGORY_SUMMIT),
    )

    class Meta:
        model = Interested
        fields = ['name', 'email', 'event_id']

    def parse_validated_data(self, validated_data):
        validated_data['event'] = validated_data.pop('event_id')
        return validated_data

    def create(self, validated_data):
        validated_data = self.parse_validated_data(validated_data)
        return super().create(validated_data)
