from django.conf import settings
from utils.drf.parsers import CamelCaseJSONParser
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from utils.drf.permissions import ConsultantConsultingPermission
from ..serializers.mixins import BasicPageNumberPagination
from ..serializers import post
from ...models import Post


class QuestionsEcosystemViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, ConsultantConsultingPermission, )
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser, )
    pagination_class = BasicPageNumberPagination
    queryset = Post.objects.all()
    serializers = {
        'default': post.PostListSerializer,
        'retrieve': post.PostDetailSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'])

    def get_queryset(self):
        return self.queryset.filter_by__type(
            settings.FORUM_CH_PROJECT)

    def list(self, request, *args, **kwargs):
        search = self.request.GET.get('search', '')
        self.queryset = self.queryset.filter_by_search(search)
        return super().list(request, *args, **kwargs)
