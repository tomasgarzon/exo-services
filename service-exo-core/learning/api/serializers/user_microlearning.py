from rest_framework import serializers

from ...models import UserMicroLearning


class UserMicroLearningSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMicroLearning
        fields = ('status', 'typeform_url', 'score', 'microlearning')
