from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from djangorestframework_camel_case import parser, render
from django_filters.rest_framework import DjangoFilterBackend

from django.conf import settings

from utils.api.doc_mixin import APIObjectMixin

from ...models import Invitation
from ..serializers import (
    invitation_status,
    invitation
)


class InvitationViewSet(APIObjectMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (render.CamelCaseJSONRenderer, )
    parser_classes = (parser.CamelCaseJSONParser, )
    model = Invitation
    lookup_field = 'hash'
    lookup_url_kwarg = 'hash'
    serializers = {
        'default': invitation.InvitationSerializer,
        'accept-{}'.format(settings.INVITATION_TYPE_AGREEMENT): invitation_status.InvitationAcceptAgreementSerializer,
        'decline-{}'.format(settings.INVITATION_TYPE_AGREEMENT): invitation_status.InvitationDeclineAgreementSerializer,
        'accept-{}'.format(settings.INVITATION_TYPE_PROFILE): invitation_status.InvitationAcceptProfileSerializer,
        'decline-{}'.format(settings.INVITATION_TYPE_PROFILE): invitation_status.InvitationDeclineProfileSerializer,
    }
    queryset = Invitation.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('hash', )

    def get_serializer_class(self):
        serializer_name = self.action
        if self.action in ['accept', 'decline']:
            invitation = self.get_object()
            serializer_name = '{}-{}'.format(self.action, invitation.type if invitation else None)

        return self.serializers.get(
            serializer_name,
            self.serializers['default'],
        )

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, hash):
        invitation = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            instance=invitation,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='decline')
    def decline(self, request, hash):
        invitation = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=invitation)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data)
