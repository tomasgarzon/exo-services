from rest_framework import serializers

from ...models import Question, Option


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ['value', 'pk']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['name', 'section', 'options', 'pk']
