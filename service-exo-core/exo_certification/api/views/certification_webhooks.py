from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from utils.drf.authentication import UsernameAuthentication

from ..serializers import PaymentsWebhookSerializer
from ...models import CertificationRequest


class CertificationRequestPaymentWebhookViewSet(
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    serializer_class = PaymentsWebhookSerializer
    permission_classes = (IsAuthenticated, )
    authentication_classes = (UsernameAuthentication, )
    queryset = CertificationRequest.objects.all()
