from rest_framework import generics

from ..serializers.training_session import TrainingSessionSerializer
from ...models import TrainingSession


class TrainingSessionListView(generics.ListAPIView):
    serializer_class = TrainingSessionSerializer
    model = TrainingSession

    def get_queryset(self):
        return self.model.objects.all()
