from rest_framework import generics

from ..serializers.language import LanguageSerializer
from ...models import Language


class LanguageListView(generics.ListAPIView):
    serializer_class = LanguageSerializer
    model = Language

    def get_queryset(self):
        return self.model.objects.all()
