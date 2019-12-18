from rest_framework import serializers

from ...models import MicroLearning


class MicroLearningSerializer(serializers.ModelSerializer):

    class Meta:
        model = MicroLearning
        fields = ('video', 'description', 'typeform_url')
