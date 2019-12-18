from django.conf import settings

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Event
from ..serializers import EventDetailSerializer, EventStatusSerializer


class EventStatusViewSet(viewsets.ModelViewSet):

    model = Event
    queryset = Event.objects.all()
    permission_classes = (IsAuthenticated, )
    lookup_field = 'uuid'
    serializers = {
        'default': EventDetailSerializer,
        'publish': EventStatusSerializer,
        'reject': EventStatusSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    @action(methods=['put'], detail=True)
    def publish(self, request, uuid):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(_status=settings.EVENT_CH_STATUS_PUBLIC)

        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def reject(self, request, uuid):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(_status=settings.EVENT_CH_STATUS_UNDER_REVIEW)

        return Response(serializer.data)
