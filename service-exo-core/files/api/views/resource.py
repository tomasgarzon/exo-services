from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

from ...models import Resource
from ..serializers.resource import ResourceAPISerializer, ResourceSerializer


class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    model = Resource
    serializers = {
        'default': ResourceSerializer,
        'list': ResourceSerializer,
        'create': ResourceAPISerializer,
    }
    queryset = Resource.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name', 'tags__name')

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        serializer = ResourceSerializer(instance=resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save(user_from=self.request.user)

    @action(detail=True, methods=['put'], url_path='tag-add')
    def tag_add(self, request, pk):
        resource = self.get_object()
        tag_name = self.request.data.get('name')
        resource.tags.add(*tag_name.split(','))
        serializer = self.get_serializer(resource)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='tag-remove')
    def tag_remove(self, request, pk):
        resource = self.get_object()
        tag_name = self.request.data.get('name')
        resource.tags.remove(*tag_name.split(','))
        serializer = self.get_serializer(resource)
        return Response(serializer.data)
