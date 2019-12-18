from django.conf import settings
from django.http import Http404

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from circles.api.views.mixins import CirclesDispatchAPIViewMixin
from circles.models import Circle
from utils.drf.permissions import ConsultantPermission

from ...models import Post
from ..serializers.mixins import BasicPageNumberPagination
from ..serializers.post import PostListSerializer


class PostCircleViewSet(
    CirclesDispatchAPIViewMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated, ConsultantPermission, )
    serializer_class = PostListSerializer
    renderer_classes = (CamelCaseJSONRenderer, )
    pagination_class = BasicPageNumberPagination
    queryset = Post.objects.all()

    def get_queryset(self):
        post_type = None
        slug = self.kwargs.get('circle_slug', None)
        post_type_mapping = {
            settings.CIRCLES_ANNOUNCEMENT_SLUG: settings.FORUM_CH_ANNOUNCEMENT,
            settings.CIRCLES_QUESTIONS_PROJECTS_SLUG: settings.FORUM_CH_PROJECT,
        }

        if slug and slug in post_type_mapping.keys():
            post_type = post_type_mapping.get(slug)
            queryset = self.queryset.filter_by__type(post_type)
        else:
            circle = Circle.all_objects.filter(slug=slug).first()

            if not circle:
                raise Http404

            self.check_circle_is_removed(circle)
            self.check_user_is_follower(self.request.user, circle)
            queryset = self.queryset.filter_by_circle(circle)

        return queryset

    def list(self, request, *args, **kwargs):
        search = self.request.GET.get('search', '')
        queryset = self.get_queryset()
        self.queryset = queryset.filter_by_search(search)

        return super().list(request, *args, **kwargs)
