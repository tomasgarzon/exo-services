from django.conf import settings
from django.utils import timezone
from django.views.generic.detail import SingleObjectMixin
from django.utils import translation

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters, pagination
from rest_framework.permissions import IsAuthenticated

from guardian.shortcuts import get_objects_for_user
from wkhtmltopdf.views import PDFTemplateView

from ..serializers.survey_filled import SurveyFilledSerializer
from ...models import SurveyFilled, Survey


class SurveyFilledViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    model = SurveyFilled
    serializer_class = SurveyFilledSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = pagination.PageNumberPagination
    page_size = 10
    page_size_query_param = 'page_size'
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'email', 'organization']
    filter_fields = ('survey',)

    def get_queryset(self):
        return self.model.objects.filter(
            survey__in=get_objects_for_user(
                self.request.user,
                settings.SURVEY_PERMS_VIEW,
                klass=Survey))


class SurveyFilledPDF(SingleObjectMixin, PDFTemplateView):
    template_name = 'survey/survey_filled_pdf.html'
    model = SurveyFilled
    raise_exception = True

    @property
    def filename(self):
        date = timezone.now().strftime('%Y-%m-%d')
        return 'response_{}.pdf'.format(date)

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        language = self.object.survey.language
        translation.activate(language)
        context = super().get_context_data(*args, **kwargs)
        return context
