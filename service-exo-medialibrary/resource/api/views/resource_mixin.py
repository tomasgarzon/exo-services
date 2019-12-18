from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters
from utils.pagination import BasicPageNumberPagination

from ..serializers import ResourceListSerializer
from ...models import Resource


class ResourceLibraryViewSetMixin(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    http_method_names = ['get']
    filter_backends = (filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend)
    pagination_class = BasicPageNumberPagination
    search_fields = ['name', 'tags__name']
    ordering_fields = ('name', 'created', 'modified')
    ordering = ('name',)
    serializer_class = ResourceListSerializer

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializer_class)
