from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import (
    viewsets, mixins, renderers, exceptions,
    filters, pagination)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.settings import api_settings

from utils.drf.authentication import UsernameAuthentication
from utils.http_response_mixin import HttpResponseMixin

from ...exceptions import OpportunityRemovedException
from ...models import Opportunity, OpportunityGroup
from ...conversation_helper import get_unread_messages
from ..serializers.opportunity import (
    OpportunitySerializer,
    ApplyOpportunitySerializer,
    OpportunityReOpenSerializer
)
from ..serializers.opportunity_detail import OpportunityDetailSerializer
from ..serializers.opportunity_list import OpportunityListSerializer, OpportunityBadgeListSerializer
from ..serializers.cancelation import CancelationSerializer
from ..serializers.conversation import (
    StartConversationSerializer,
    StartConversationApplicantSerializer,
)


class Paginator(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class OpportunityViewSet(HttpResponseMixin, viewsets.ModelViewSet):

    model = Opportunity
    permission_classes = (IsAuthenticated, )
    renderer_classes = (
        CamelCaseJSONRenderer,
        renderers.JSONRenderer,
    )
    pagination_class = Paginator
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'exo_role__name', 'id']
    serializers = {
        'default': OpportunitySerializer,
        'list': OpportunityListSerializer,
        'retrieve': OpportunityDetailSerializer,
        'admin': OpportunityDetailSerializer,
        'destroy': CancelationSerializer,
        'close': CancelationSerializer,
        're_open': OpportunityReOpenSerializer,
        'apply': ApplyOpportunitySerializer,
        'create_conversation': StartConversationSerializer,
        'start_conversation_with_applicant': StartConversationApplicantSerializer,
        'preview': OpportunitySerializer,
    }

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ValidationError:
            exc = exceptions.PermissionDenied()
            response = self.handle_exception(exc)
            self.response = self.finalize_response(
                request, response, *args, **kwargs)
            return self.response
        except OpportunityRemovedException as err:
            return self.gone_410_response(
                classname=err.opportunity.__class__.__name__,
                object_id=err.opportunity.pk)

    def check_is_removed(self):
        if self.action == 'retrieve':
            opportunity = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
            if opportunity.is_removed:
                raise OpportunityRemovedException(opportunity, 'Opportunity removed')

    def get_queryset(self):
        self.check_is_removed()
        user = self.request.user
        published_by_you = self.request.GET.get('published_by_you')
        only_published_by_you = self.request.GET.get('only_published_by_you')  # only for instrumentation
        action_published = self.action in ['list', 'update', 'close', 're_open', 'destroy'] and published_by_you
        action_admin = self.action == 'admin'
        action_retrieve = self.action == 'retrieve'

        if action_retrieve:
            queryset = self.model.objects.filter_for_admin()
        elif action_published or action_admin:
            if user.is_superuser:
                queryset = self.model.objects.filter_for_admin()
            else:
                q1 = Q(created_by=user)
                q2 = Q(group__managers=user)
                queryset = self.model.objects.filter(q1 | q2).not_draft().not_removed()

        elif only_published_by_you:
            queryset = self.model.objects.filter(created_by=user)
        else:
            queryset = self.model.objects.all_my_opportunities(user)

        if queryset.exists():
            queryset = queryset.distinct()

        return queryset

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def perform_create(self, serializer):
        serializer.save(
            user_from=self.request.user,
        )

    def perform_update(self, serializer):
        serializer.save(
            user_from=self.request.user,
        )

    def add_unread_messages(self, page, user):
        opps = [opp.uuid.__str__() for opp in page]
        response = get_unread_messages(opps, user)
        for conv_data in response:
            opp_data = list(filter(
                lambda x: x.uuid.__str__() == conv_data['uuid'], page))
            try:
                opp_data[0].num_messages = conv_data['numMessages']
            except IndexError:
                continue
        return page

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.add_unread_messages(page, request.user)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        queryset = self.add_unread_messages(queryset, request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_actions = instance.user_actions(request.user)
        if settings.OPPORTUNITIES_ACTION_CH_REMOVE not in user_actions:
            raise ValidationError('Opportunity can not be removed')
        serializer = self.get_serializer(
            self.get_object(), data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(instance, serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        opportunity = self.get_object()
        opportunity.see(request.user, notify=False)
        return response

    def perform_destroy(self, instance, serializer):
        instance.remove(
            self.request.user,
            comment=serializer.validated_data.get('comment'),
        )

    @action(detail=True, methods=['put'])
    def send(self, request, pk):
        queryset = self.model.objects.all()
        opportunity = get_object_or_404(queryset, pk=pk)
        opportunity.send(request.user)
        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def apply(self, request, pk):
        opportunity = self.get_object()
        serializer = self.get_serializer(
            instance=opportunity, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=request.user,
        )
        serializer = OpportunityDetailSerializer(
            opportunity, context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def close(self, request, pk):
        opportunity = self.get_object()
        serializer = self.get_serializer(
            instance=opportunity, data=request.data)
        serializer.is_valid(raise_exception=True)
        valid = opportunity.can_do_actions(
            request.user, settings.OPPORTUNITIES_ACTION_CH_CLOSE, False)
        if not valid:
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't close"],
            })
        opportunity.close(request.user, serializer.validated_data.get('comment'))
        serializer = self.serializers.get('admin')(
            instance=opportunity,
            context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_name='re-open', url_path='re-open')
    def re_open(self, request, pk):
        opportunity = self.get_object()
        serializer = self.get_serializer(
            instance=opportunity, data=request.data)
        serializer.is_valid(raise_exception=True)
        valid = opportunity.can_do_actions(
            request.user, settings.OPPORTUNITIES_ACTION_CH_RE_OPEN, False)
        if not valid:
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't re open"],
            })
        opportunity.re_open(request.user, serializer.validated_data.get('deadline_date'))
        serializer = self.serializers.get('admin')(
            instance=opportunity,
            context=self.get_serializer_context())
        response_data = serializer.data
        response_data['numApplicants'] = opportunity.applicants_info.count()
        response_data['numMessages'] = opportunity.get_unread_messages(request.user)
        return Response(response_data)

    @action(detail=True, methods=['get'])
    def admin(self, request, pk):
        opportunity = self.get_object()
        serializer = self.get_serializer(
            instance=opportunity)
        data = serializer.data
        opportunity.see(request.user, notify=False)
        return Response(data)

    @action(detail=True, methods=['put'])
    def see(self, request, pk):
        opportunity = self.get_object()
        if not opportunity.can_see(request.user, raise_exceptions=False):
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: ["User can't see the post"],
            })
        opportunity.see(request.user)
        return Response()

    @action(detail=True, methods=['post'])
    def create_conversation(self, request, pk):
        opportunity = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            opportunity=opportunity,
            user_from=request.user,
        )
        return Response()

    @action(
        detail=True, methods=['post'],
        url_name='start-conversation-applicant',
        url_path='start-conversation-applicant/(?P<applicant_pk>\\d+)')
    def start_conversation_with_applicant(self, request, pk, applicant_pk):
        opportunity = self.get_object()
        applicant = opportunity.applicants_info.get(pk=applicant_pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            opportunity=opportunity,
            user_to=applicant.user,
            user_from=request.user,
        )
        return Response()

    @action(detail=False, methods=['post'])
    def preview(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        opportunity = serializer.save(
            user_from=request.user,
            draft=True,
        )
        OutputSerializer = self.serializers['retrieve']
        serializer = OutputSerializer(
            opportunity, context=self.get_serializer_context())
        return Response(serializer.data)


class OpportunityGroupViewSet(OpportunityViewSet):

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(OpportunityGroup, id=group_id)
        return self.model.objects.filter(group=group).not_draft().not_removed()


class OpportunityBadgesViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    model = Opportunity
    serializer_class = OpportunityBadgeListSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (UsernameAuthentication, )

    def get_queryset(self):
        return self.model.objects.filter_by_applicants_assigned()
