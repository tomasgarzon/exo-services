from django.conf import settings
from django.http import HttpResponse
from django.utils import translation

from rest_framework import viewsets, pagination, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from guardian.shortcuts import get_objects_for_user

from ..serializers.survey import SurveySerializer, SurveyDetailSerializer
from ...models import Survey


class SurveyViewSet(viewsets.ModelViewSet):

    model = Survey
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination
    page_size = 10
    page_size_query_param = 'page_size'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    serializers = {
        'default': SurveyDetailSerializer,
        'list': SurveyDetailSerializer,
        'create': SurveySerializer,
        'update': SurveySerializer,
    }

    def get_queryset(self):
        return get_objects_for_user(
            self.request.user,
            settings.SURVEY_PERMS_VIEW,
            klass=self.model)

    def get_serializer_class(self):
        return self.serializers.get(
            self.action, self.serializers['default'])

    def perform_create(self, serializer):
        return serializer.save(
            user_from=self.request.user)

    def perform_update(self, serializer):
        return serializer.save(
            user_from=self.request.user)

    @action(detail=True, methods=['get'], url_path='download-csv')
    def download_csv(self, request, pk):
        instance = self.get_object()
        language = instance.language
        translation.activate(language)
        xlsx_wrapper = instance.get_report_csv()
        response = HttpResponse(xlsx_wrapper.read(), content_type=xlsx_wrapper.content_type)
        response['Content-Disposition'] = xlsx_wrapper.content_disposition
        return response


class CheckSlugAPIView(APIView):

    def get(self, request, format=None):
        slug = request.GET.get('slug', '')
        exists = Survey.objects.filter(slug=slug).exists()
        return Response(exists)
