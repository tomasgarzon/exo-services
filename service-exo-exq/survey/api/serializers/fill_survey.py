from rest_framework import serializers

from industry.models import Industry

from ...models import Question, Option


class AnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all())
    option = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all())


class FillSurveySerializer(serializers.Serializer):

    name = serializers.CharField()
    organization = serializers.CharField(
        required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField()
    answers = AnswerSerializer(many=True)
    industry = serializers.PrimaryKeyRelatedField(
        queryset=Industry.objects.all(),
        required=False)

    def create(self, validated_data):
        survey = validated_data.pop('survey')
        return survey.fill(
            **validated_data)
