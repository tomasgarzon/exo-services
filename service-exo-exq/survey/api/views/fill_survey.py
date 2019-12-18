from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication

from utils.drf.authentication import CsrfExemptSessionAuthentication

from ..serializers.fill_survey import FillSurveySerializer
from ...models import Survey


class FillSurveyAPIView(SingleObjectMixin, APIView):
    model = Survey
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    serializer_class = FillSurveySerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    @method_decorator(csrf_exempt)
    def post(self, request, slug, format=None):
        survey = self.get_object()
        serializer = FillSurveySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        survey_filled = serializer.save(
            survey=survey)
        data = {}

        if survey.show_results:
            data = {
                'total': survey_filled.total,
                'show_results': survey_filled.survey.show_results,
            }

        return Response(data)
