from rest_framework import serializers

from ...models import TrainingSession


class TrainingSessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrainingSession
        fields = ['name', 'id']
