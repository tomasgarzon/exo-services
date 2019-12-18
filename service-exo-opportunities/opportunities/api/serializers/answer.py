from rest_framework import serializers

from ...models import Answer
from .question import QuestionSerializer


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['pk', 'response', 'response_text', 'question']
        read_only_fields = ['pk']


class AnswerQuestionDetailSerializer(AnswerSerializer):

    question = QuestionSerializer()
