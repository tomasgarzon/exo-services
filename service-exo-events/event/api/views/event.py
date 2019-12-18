from django.conf import settings

from rest_framework import viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.certification_helpers import CertificationWorkshopWrapper
from utils.drf.authentication import UsernameAuthentication

from ...models import Event
from ...helpers import EventPermissionHelper
from ...tasks import SummitRequestTask
from ..serializers import (
    EventAvailableSerializer,
    EventTypesSerializer,
    EventChangeStatusSerializer,
    EventDetailSerializer,
    EventSerializer,
    EventListSerializer,
    RequestSummitSerializer,
)
from .custom_pagination import StandardResultsSetPagination


class EventViewSet(viewsets.ModelViewSet):
    model = Event
    permission_classes = (IsAuthenticated, )
    pagination_class = StandardResultsSetPagination
    authentication_classes = (JSONWebTokenAuthentication, UsernameAuthentication, )
    lookup_field = 'uuid'
    serializers = {
        'default': EventListSerializer,
        'create': EventSerializer,
        'update': EventSerializer,
        'change_status': EventChangeStatusSerializer,
        'retrieve': EventDetailSerializer,
        'permissions': EventAvailableSerializer,
        'events_types': EventTypesSerializer,
        'request_summit': RequestSummitSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_queryset(self):
        return self.model.objects.filter_by_user(self.request.user).distinct()

    def check_edit_permissions(self):
        event = self.get_object()
        can_edit = self.request.user.has_perm(
            settings.EVENT_PERMS_EDIT_EVENT,
            event,
        )
        if not can_edit and self.request.user.uuid != event.created_by.uuid:
            raise exceptions.PermissionDenied

    def create(self, request, *args, **kwargs):
        helper = EventPermissionHelper()
        can_create = helper.has_perm(
            request.user,
            'create_{}'.format(request.data.get('category')),
        )
        if not can_create:
            raise exceptions.PermissionDenied

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user_from=self.request.user)

    @action(methods=['get'], detail=False)
    def permissions(self, request):
        helper = EventPermissionHelper()
        user_objects = helper.get_events_available(request.user)
        serializer = EventAvailableSerializer(
            list(filter(lambda x: x[0] in user_objects, settings.EVENT_TYPE_CHOICES)),
            many=True,
        )
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def events_types(self, request):
        event_available_data = []
        helper = EventPermissionHelper()
        for event_type in settings.EVENT_TYPE_CHOICES:
            event_available_data.append([
                event_type[0],
                event_type[1],
                helper.has_perm(request.user, 'create_{}'.format(event_type[0])),
            ])

        serializer = EventTypesSerializer(event_available_data, many=True)
        return Response(serializer.data)

    @action(methods=['put'], detail=True)
    def change_status(self, request, uuid):
        self.check_edit_permissions()
        serializer = self.get_serializer(
            instance=self.get_object(),
            data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_from=request.user)

        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def request_summit(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        SummitRequestTask().s(
            user_uuid=self.request.user.uuid.__str__(),
            **serializer.validated_data,
        ).apply_async()

        return Response(serializer.data)

    def perform_destroy(self, instance):
        self.check_edit_permissions()
        instance.status = (self.request.user, settings.EVENT_CH_STATUS_DELETED)

    @action(methods=['post'], detail=True, url_path='send-certificates')
    def send_certificates(self, request, uuid):
        event = self.get_object()
        certification_wrapper = CertificationWorkshopWrapper(event)
        certification_wrapper.release_group_credential(request.user, event)
        return Response()
