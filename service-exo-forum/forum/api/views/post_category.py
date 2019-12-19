from django.http import Http404

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from utils.drf.permissions import ConsultantPermission

from .mixins import CategoryDispatchAPIViewMixin
from ...models import Post, Category
from ..serializers.mixins import BasicPageNumberPagination
from ..serializers.post import PostListSerializer


class PostCategoryViewSet(
    CategoryDispatchAPIViewMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated, ConsultantPermission, )
    serializer_class = PostListSerializer
    pagination_class = BasicPageNumberPagination
    queryset = Post.objects.all()

    def get_queryset(self):
        slug = self.kwargs.get('slug', None)

        category = Category.all_objects.filter(slug=slug).first()

        if not category:
            raise Http404

        self.check_category_is_removed(category)
        self.check_user_is_follower(self.request.user, category)
        queryset = self.queryset.filter_by_category(category)

        return queryset

    def list(self, request, *args, **kwargs):
        search = self.request.GET.get('search', '')
        queryset = self.get_queryset()
        self.queryset = queryset.filter_by_search(search)

        return super().list(request, *args, **kwargs)
