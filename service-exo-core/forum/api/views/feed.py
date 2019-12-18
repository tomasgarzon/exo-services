from django.conf import settings
from actstream.models import Follow
from django.db.models import Q, Subquery, IntegerField
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import Cast
from django.contrib.auth import get_user_model
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from rest_framework import generics

from circles.models import Circle

from ..serializers.feed import PostFeedSerializer
from ..serializers.mixins import BasicPageNumberPagination
from ...models import Post

User = get_user_model()


class PostFeedListView(generics.ListAPIView):
    queryset = Post.objects.all()
    pagination_class = BasicPageNumberPagination
    serializer_class = PostFeedSerializer
    renderer_classes = (CamelCaseJSONRenderer, )

    def get_queryset(self):
        queries = [Q(_type=settings.FORUM_CH_ANNOUNCEMENT)]
        if self.request.user.has_perm(settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_CONSULTING):
            queries.append(
                Q(_type=settings.FORUM_CH_PROJECT))
        query = Follow.objects.following_qs(
            self.request.user, Circle
        ).annotate(as_integer=Cast('object_id', IntegerField()))
        queries.append(Q(
            _type=settings.FORUM_CH_CIRCLE,
            content_type=ContentType.objects.get_for_model(Circle),
            object_id__in=Subquery(query.values('as_integer'))))
        query_final = Q()
        for query_q in queries:
            query_final |= query_q
        return self.queryset.exclude(
            _type=settings.FORUM_CH_QA_SESSION
        ).filter(query_final).order_by('-modified')
