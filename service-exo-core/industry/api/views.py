from rest_framework import generics
from rest_framework.response import Response
from utils.drf import DALAutocompleteSelect2Public

from .serializers import IndustrySerializer, IndustrySelect2Serializer
from ..models import Industry


class IndustryAPIView(DALAutocompleteSelect2Public):

    model = Industry


class IndustryListAPIView(generics.ListAPIView):

    model = Industry
    serializer_class = IndustrySerializer

    def get_queryset(self):
        return self.model.objects.filter(public=True)


class IndustrySelect2(IndustryListAPIView):
    serializer_class = IndustrySelect2Serializer

    def get(self, request, *args, **kwargs):
        data = [
            {
                'id': ind.id,
                'text': ind.name, }
            for ind in self.model.objects.filter(
                public=True,
                name__icontains=request.GET.get('q', ''),
            )
        ]
        return Response(data)
