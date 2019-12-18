from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import generics, serializers
from rest_framework.filters import SearchFilter

from core.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'name',
            'native_name',
            'code_2',
            'code_3',
            'flag',
        ]


class CountryListView(generics.ListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
    renderer_classes = (CamelCaseJSONRenderer, )
    filter_backends = (SearchFilter, )
    search_fields = ('name', 'native_name', 'code_2', 'code_3')
