from django.conf import settings
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..serializers.cohort import CohortSerializer
from ...models import CertificationCohort


class CohortListView(generics.ListAPIView):
    serializer_class = CohortSerializer
    queryset = CertificationCohort.objects.all()
    renderer_classes = (CamelCaseJSONRenderer, )
    permission_classes = (AllowAny, )

    def get_queryset(self):
        return self.queryset.filter(
            status=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_OPEN
        )

    def list(self, request, *args, **kwargs):
        level = self.request.GET.get(
            'level', settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
        )
        self.queryset = self.get_queryset().filter(
            certification__level=level
        ).order_by('date')
        return super().list(request, *args, **kwargs)
