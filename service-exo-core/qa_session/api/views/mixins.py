from django.contrib.auth import get_user_model
from django.db.models import Count

from utils.drf.parsers import CamelCaseJSONParser
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from forum.api.serializers import post
from forum.models import Post

from ..serializers.question import QAQuestionWriteSerializer

User = get_user_model()


class BasicPageNumberPagination(
        PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'


class QASessionGenericViewMixin(
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser, )

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'])


class QASessionQuestionGenericMixin(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin):
    pagination_class = BasicPageNumberPagination
    queryset = Post.objects.all().annotate(comments=Count('answers'))
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['comments', 'modified']

    serializers = {
        'default': post.PostListSerializer,
        'retrieve': post.PostDetailSerializer,
        'create': QAQuestionWriteSerializer,
        'update': QAQuestionWriteSerializer,
        'destroy': QAQuestionWriteSerializer,
    }

    def get_queryset(self):
        ordering = self.request.query_params.get('ordering', 'comments')
        qs = self.queryset
        if ordering and ordering in self.ordering_fields:
            qs = qs.order_by(ordering)
        return qs

    def list(self, request, *args, **kwargs):
        search = self.request.GET.get('search', '')
        queryset = self.get_queryset()
        self.queryset = queryset.filter_by_search(search)
        return super().list(request, *args, **kwargs)
