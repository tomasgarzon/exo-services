from django.conf import settings
from django.http import Http404
from django.db.models import Count

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.drf.mixins.api_no_permissions_response import ApiNoPermissionsResponseMixin

from ..serializers.post import PostCreateSerializer
from .mixins import BasicPageNumberPagination
from ..serializers.circle import CircleSerializer, CircleNoQuestionsSerializer
from ..serializers.circle_create import CircleCreateSerializer
from ...helpers import get_question_projects_circle, get_announcements_circle
from ...models import Circle


def circle_displayed(c):
    not_certified_circle = c.type != settings.CIRCLES_CH_TYPE_CERTIFIED
    certified_with_posts = c.type == settings.CIRCLES_CH_TYPE_CERTIFIED and c.total_posts > 0
    return not_certified_circle or certified_with_posts


class ForumCategoryViewSet(
        ApiNoPermissionsResponseMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )
    pagination_class = BasicPageNumberPagination
    queryset = Circle.objects.all()
    lookup_field = 'slug'
    serializers = {
        'default': CircleSerializer,
        'create': CircleCreateSerializer,
        'update': CircleCreateSerializer,
        'create_post': PostCreateSerializer,
        'join_circle': CircleNoQuestionsSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action, self.serializers['default'])

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            filter_status = self.request.GET.get(
                'status', settings.CIRCLES_PARAM_STATUS_CH_SUBSCRIBED)
            if filter_status == settings.CIRCLES_PARAM_STATUS_CH_NOT_SUBSCRIBED:
                qs = self.queryset.filter_not_subscribed(user)
            else:
                qs = self.queryset.filter_subscribed(user)
        else:
            qs = self.queryset.filter_readable(user)

        return qs.annotate(total_posts=Count('posts'))

    def retrieve(self, request, *args, **kwargs):
        user = self.request.user
        slug = kwargs['slug']
        try:
            instance = self.get_object()
        except Http404:
            if slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
                instance = get_announcements_circle()
            elif slug == settings.CIRCLES_QUESTIONS_PROJECTS_SLUG and \
                    user.has_perm(settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_CONSULTING):
                instance = get_question_projects_circle()
            else:
                raise Http404
        serializer = self.get_serializer_class()(
            instance, context=self.get_serializer_context())
        return Response(serializer.data, status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        circles = list(self.get_queryset())
        filter_status = self.request.GET.get(
            'status', settings.CIRCLES_PARAM_STATUS_CH_SUBSCRIBED)

        #  TODO: Transform virtual circles into real ones in further iterations
        if filter_status != settings.CIRCLES_PARAM_STATUS_CH_NOT_SUBSCRIBED:
            circles.append(get_announcements_circle())
            if user.is_superuser or user.has_certified_role(settings.ROL_CH_EXO_FOUNDATIONS):
                circles.append(get_question_projects_circle())
            circles = list(filter(lambda x: circle_displayed(x), circles))

        page = self.paginate_queryset(circles)
        if page is None:
            serializer = self.get_serializer_class()(
                circles, many=True, context=self.get_serializer_context())
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            serializer = self.get_serializer_class()(
                circles, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='create', url_name='create')
    def create_post(self, request, slug):
        data = self.request.data
        if not slug == settings.CIRCLES_ANNOUNCEMENT_SLUG:
            circle = self.get_object()
            data['circle'] = circle.pk
        serializer = self.get_serializer_class()(
            data=data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, slug):
        user = self.request.user
        circle = self.get_object()
        circle.user_can_join(user)
        if not circle.is_user_in_followers(user):
            circle.add_user(user)
        serializer = self.get_serializer_class()(
            circle, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='leave')
    def leave(self, request, slug):
        user = self.request.user
        circle = self.get_object()
        circle.user_can_leave(user)
        if circle.is_user_in_followers(user):
            circle.remove_user(user)
        serializer = self.get_serializer_class()(
            circle, context=self.get_serializer_context())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
