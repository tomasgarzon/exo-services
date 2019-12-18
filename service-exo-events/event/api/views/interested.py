from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework import permissions
from rest_framework.authentication import BasicAuthentication
from rest_framework.generics import CreateAPIView

from utils.drf.authentication import CsrfExemptSessionAuthentication

from ...models import Event, Interested
from ..serializers.interested import (
    InterestedListSerializer,
    InterestedCreateSerializer,
)


class InterestedListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    model = Interested
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InterestedListSerializer

    def get_event(self):
        return get_object_or_404(Event, uuid=self.kwargs.get('event_id'))

    def get_queryset(self):
        return self.get_event().interested.all()


class InterestedCreateAPIView(CreateAPIView):
    queryset = Interested.objects.all()
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = InterestedCreateSerializer
