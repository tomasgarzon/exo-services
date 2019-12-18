from rest_framework import serializers

from ...models.microlearning_average import MicroLearningAverage
from ...models.user_microlearning import UserMicroLearning
from ...helpers import serialize_personal_quiz


class PersonalQuizSerializer(serializers.Serializer):

    url = serializers.SerializerMethodField()
    teamRatings = serializers.SerializerMethodField()
    personalRating = serializers.SerializerMethodField()

    class Meta:
        model = UserMicroLearning

    def get_url(self, obj):
        return obj.typeform_url

    def get_teamRatings(self, obj):
        pass

    def get_personalRating(self, obj):
        pass

    def to_representation(self, instance):
        representation_data = super().to_representation(instance)
        microlearning_average = MicroLearningAverage(
            step_stream=instance.microlearning.step_stream,
            user=instance.user,
            team=instance.team,
        )
        serialized_data = serialize_personal_quiz(microlearning_average)
        return {
            'url': representation_data.get('url'),
            'teamRatings': serialized_data.get('teamRatings'),
            'personalRating': serialized_data.get('personalRating')
        }
