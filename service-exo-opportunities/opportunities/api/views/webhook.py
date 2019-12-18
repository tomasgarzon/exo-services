from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from utils.drf.authentication import UsernameAuthentication

from ..serializers.conversation import (
    FirstMessageConversation)
from ...models import Opportunity


class OpportunityWebhookViewSet(
        viewsets.GenericViewSet):
    queryset = Opportunity.objects.all()
    authentication_classes = (UsernameAuthentication, )
    renderer_classes = (CamelCaseJSONRenderer, )
    permission_classes = (IsAuthenticated,)

    serializers = {
        'default': None,
        'first_message': FirstMessageConversation,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    @action(detail=False, methods=['post'], url_path='first-message', url_name='first-message')
    def first_message(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response()
