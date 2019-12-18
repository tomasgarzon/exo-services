from django.http import Http404
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from circles.api.views.mixins import CirclesDispatchAPIViewMixin
from forum.api.serializers.post_legacy import PostLegacySerializer

from ..serializers.post import PostDetailSerializer
from ...models import Post


class PostSlugViewSet(
        CirclesDispatchAPIViewMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    serializer_class = PostDetailSerializer
    queryset = Post.all_objects.all()
    renderer_classes = (CamelCaseJSONRenderer,)
    permission_classes = (IsAuthenticated, )
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_circle_is_removed(instance.circle)
        self.check_user_is_follower(request.user, instance.circle)
        can_see = instance.can_see(request.user, raise_exceptions=False)
        if can_see and instance.is_removed:
            return self.gone_410_response(
                classname=instance.__class__.__name__)
        if not can_see:
            raise Http404
        return super().retrieve(request, *args, **kwargs)

    """
    Maintains backwards compatibility for front-end
    """
    @action(detail=True, methods=['get'], url_path='legacy-details')
    def legacy_details(self, request, slug):
        instance = self.get_object()
        serializer = PostLegacySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
