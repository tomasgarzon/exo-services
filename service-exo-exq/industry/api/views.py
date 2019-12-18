from rest_framework import generics

from .serializers import IndustrySerializer
from ..models import Industry


class IndustryListAPIView(generics.ListAPIView):

    model = Industry
    serializer_class = IndustrySerializer
    pagination_class = None

    def get_queryset(self):
        return self.model.objects.all()
