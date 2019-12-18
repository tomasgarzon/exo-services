from django.conf import settings
from django.db.models import Case, Value, When, IntegerField

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from exo_certification.api.serializers.certification_role import CertificationRoleWithOrderSerializer
from exo_role.models import CertificationRole


class CertsListView(generics.ListAPIView):
    serializer_class = CertificationRoleWithOrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        codes = [
            settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS,
            settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
            settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH,
        ]
        return CertificationRole.objects.filter(code__in=codes) \
            .annotate(
                order=Case(
                    When(
                        code=settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS,
                        then=Value(1),
                    ),
                    When(
                        code=settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
                        then=Value(2),
                    ),
                    When(
                        code=settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH,
                        then=Value(3),
                    ),
                    default=0,
                    output_field=IntegerField(),
                )) \
            .order_by('order')
