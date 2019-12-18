from rest_framework import generics

from exo_role.models import Category

from ..serializers.roles import CategorySerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
