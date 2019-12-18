from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, permissions, generics
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from utils.certification_helpers import CertificationWorkshopWrapper
from utils.drf.authentication import CsrfExemptSessionAuthentication, UsernameAuthentication
from opportunities.serializers import AddParticipantFromOpportunitySerializer

from ...models import Event, Participant
from ..serializers.event_add_participant import (
    AddParticipantSerializer,
    AddParticipantPublicSerializer,
    UpdateParticipantSerializer,
    UploadParticipantSerializer,
)
from ..serializers.participant_serializer import (
    ParticipantSerializer,
    ParticipantBadgeListSerializer,
)


class EventPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        event = get_object_or_404(Event, uuid=view.kwargs.get('event_id'))
        return request.user.has_perm(
            settings.EVENT_PERMS_EDIT_EVENT,
            event,
        )


class ParticipantViewSet(viewsets.ModelViewSet):

    model = Participant
    permission_classes = (permissions.IsAuthenticated & EventPermission,)
    authentication_classes = (UsernameAuthentication, JSONWebTokenAuthentication)
    serializers = {
        'default': ParticipantSerializer,
        'create': AddParticipantSerializer,
        'update': UpdateParticipantSerializer,
        'retrieve': ParticipantSerializer,
        'upload': UploadParticipantSerializer,
        'add_from_opportunity': AddParticipantFromOpportunitySerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_event(self):
        return get_object_or_404(Event, uuid=self.kwargs.get('event_id'))

    def get_queryset(self):
        return self.get_event().participants.all()

    def perform_create(self, serializer):
        serializer.save(user_from=self.request.user, event=self.get_event())

    @action(methods=['post'], detail=False, url_path='upload')
    def upload(self, request, event_id):
        event = self.get_event()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        participants = serializer.save(user_from=request.user, event=event)
        new_serializer = self.serializers.get('default')(
            participants,
            many=True)
        return Response(new_serializer.data)

    @action(methods=['post'], detail=True, url_path='generate-certificate')
    def generate_certificate(self, request, event_id, pk):
        instance = self.get_object()
        certification_wrapper = CertificationWorkshopWrapper(instance.event)
        certification_wrapper.release_simple_credential(request.user, instance)
        return Response()

    @action(methods=['post'], detail=False)
    def add_from_opportunity(self, request, event_id):
        event = self.get_event()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        return Response()


class ParticipantPublicViewSet(CreateAPIView):
    queryset = Participant.objects.all()
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = AddParticipantPublicSerializer


class ParticipantBadgesViewSet(generics.ListAPIView):

    authentication_classes = (UsernameAuthentication, )
    serializer_class = ParticipantBadgeListSerializer
    permission_classes = (IsAuthenticated, )
    pagination_class = None

    def get_queryset(self):
        today = timezone.now().date()
        speakers_roles = Participant.get_role_by_name(settings.EVENT_PARTICIPANT_NAME)
        filters = {
            'event___status': settings.EVENT_CH_STATUS_PUBLIC,
            'event__end__isnull': False,
            'event__end__lte': today,
        }
        return Participant.objects.filter_by_status(
            settings.EVENT_CH_ROLE_STATUS_ACTIVE,
        ).filter(**filters).exclude(
            exo_role__code__in=speakers_roles,
        )
