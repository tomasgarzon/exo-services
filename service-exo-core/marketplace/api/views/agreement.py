from django.conf import settings

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from djangorestframework_camel_case.parser import CamelCaseJSONParser

from agreement.models import Agreement
from agreement.api.serializers.agreement import AgreementSerializer
from utils.drf.permissions import ConsultantPermission


class MarketplaceAgreementViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Agreement.objects.filter_by_domain_marketplace().filter_by_status_active()
    renderer_classes = (CamelCaseJSONRenderer,)
    parser_classes = (CamelCaseJSONParser,)
    permission_classes = (IsAuthenticated, ConsultantPermission)

    serializers = {
        'default': AgreementSerializer,
        'retrieve': AgreementSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        request.user.see_section(settings.EXO_ACCOUNTS_MARKETPLACE_SECTION)
        return response

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk):
        instance = self.get_object()
        request.user.sign_agreement(instance)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk):
        instance = self.get_object()
        request.user.reject_agreement(instance)
        return Response(status=status.HTTP_200_OK)
