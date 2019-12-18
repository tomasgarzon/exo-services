from django.http import Http404
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from djangorestframework_camel_case.parser import CamelCaseJSONParser
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError

from utils.http_response_mixin import HttpResponseMixin
from circles.api.views.mixins import BasicPageNumberPagination

from ...models import Post
from ..serializers import post, answer
from ...tasks.answer_tasks import MarkAnswerAsReadTask


class PostViewSet(
        HttpResponseMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    """
    API REST for post management that provides these actions:

    `retrieve`, `update`, `destroy`, `reply`.

    retrieve:
    Get a post instance.

    update:
    Update a post instance.

    destroy:
    Destroy a post instance.

    reply
    Create a new answer to post instance
    """
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()
    serializers = {
        'default': post.PostListSerializer,
        'retrieve': post.PostDetailSerializer,
        'update': post.PostUpdateSerializer,
        'reply': answer.AnswerCreateUpdateSerializer,
        'answers': answer.AnswerPostSerializer,
    }
    renderer_classes = (CamelCaseJSONRenderer, )
    parser_classes = (CamelCaseJSONParser,)
    pagination_class = BasicPageNumberPagination

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def perform_update(self, serializer):
        serializer.save(
            user_from=self.request.user,
        )

    def perform_destroy(self, instance):
        instance.mark_as_removed(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = Post.all_objects.get(pk=kwargs['pk'])
        except Post.DoesNotExist:
            raise Http404
        can_see = instance.can_see(request.user, raise_exceptions=False)
        if can_see and instance.is_removed:
            return self.gone_410_response(
                classname=instance.__class__.__name__)
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='answers')
    def answers(self, request, pk):
        instance = self.get_object()
        if not instance.can_see(request.user, raise_exceptions=False):
            raise Http404
        answers = instance.answers.all()
        page = self.paginate_queryset(answers)

        if page is None:
            serializer = self.get_serializer(
                answers, many=True, context={'request': request})
            response = Response(serializer.data)
        else:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            response = self.get_paginated_response(serializer.data)

        MarkAnswerAsReadTask().s(
            answer_pks=[item['pk'] for item in response.data['results']],
            user_pk=self.request.user.pk,
            post_pk=pk,
        ).apply_async()
        return response

    @action(detail=True, methods=['post'], url_path='reply')
    def reply(self, request, pk):
        instance = self.get_object()
        if not instance.can_reply(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't reply the post"],
            })
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_from=request.user, post=post)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='like')
    def like(self, request, pk):
        instance = self.get_object()
        if not instance.can_vote(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't vote the post"],
            })
        if not instance.have_liked(request.user):
            instance.do_like(request.user)
        serializer = post.PostDetailSerializer(
            instance, context={'request': self.request})
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='unlike')
    def unlike(self, request, pk):
        instance = self.get_object()
        if not instance.can_vote(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't vote the post"],
            })
        if instance.have_liked(request.user):
            instance.clear_previous_votes(request.user)
        serializer = post.PostDetailSerializer(
            instance, context={'request': self.request})
        return Response(serializer.data)
