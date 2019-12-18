from rest_framework import generics, viewsets
from rest_framework import permissions

from ..serializers import CategorySerializer
from ...models import Category


class CategoryViewSet(generics.ListAPIView, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get']
