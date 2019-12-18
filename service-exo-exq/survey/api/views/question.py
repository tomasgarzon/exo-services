from rest_framework import generics

from ..serializers.question import QuestionSerializer
from ...models import Question


class QuestionListView(generics.ListAPIView):
    model = Question
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    pagination_class = None
