from rest_framework import viewsets, renderers, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from ..signals_define import signal_website_update
from . import serializers
from ..models import Page
from .. import process


class PageViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    queryset = Page.objects.all()
    renderer_classes = (
        CamelCaseJSONRenderer, renderers.JSONRenderer,)
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    serializers = {
        'default': serializers.PageSerializer,
        'create': serializers.CreatePageSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    @action(methods=['put'], detail=True, url_path='preview')
    def preview(self, request, uuid):
        page = self.get_object()
        serializer = self.get_serializer(page, data=request.data)
        serializer.is_valid(raise_exception=True)
        process.build_preview(
            page_type=page.page_type,
            data=serializer.validated_data,
            uuid=page.uuid)
        output_serializer = serializers.PublicPageSerializer(instance=page)
        return Response(output_serializer.data)

    @action(methods=['get'], detail=False, url_path='validate')
    def validate(self, request):
        slug = request.GET.get('value')
        exists = Page.objects.filter(slug=slug).exists()
        return Response(not exists)

    @action(methods=['put'], detail=True, url_path='change-status', url_name='change-status')
    def change_status(self, request, uuid):
        page = self.get_object()
        page.published = not page.published
        page.save()
        signal_website_update.send(
            sender=Page,
            instance=page)
        return Response(page.published)


class PublicPageViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    queryset = Page.objects.all()
    renderer_classes = (
        CamelCaseJSONRenderer, renderers.JSONRenderer,)
    lookup_field = 'uuid'
    serializer_class = serializers.PublicPageSerializer
