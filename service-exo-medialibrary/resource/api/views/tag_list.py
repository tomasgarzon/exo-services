from rest_framework import generics, viewsets
from rest_framework import permissions

from ..serializers import TagSerializer
from ...models import Tag


class TagViewSet(generics.ListAPIView, viewsets.ModelViewSet):
    queryset = Tag.objects.select_related('category').all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ["get"]
