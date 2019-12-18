from django.core.exceptions import ValidationError

from rest_framework import viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers.opportunity_applicant_actions import (
    AssignOpportunitySerializer, RejectOpportunitySerializer)
from ..serializers.applicant import OpportunityApplicantSerializer
from ..serializers.opportunity_detail import (
    OpportunityDetailSerializer)
from ..serializers.applicant_sow import (
    ApplicantEditSowSerializer,
    RequesterEditSowSerializer,
    InitialApplicantSowSerializer)
from ..serializers.feedback import FeedbackApplicantSerializer
from ...models import Applicant
from ...sow_helpers import init_sow_from_applicant


class ApplicantViewSet(
        viewsets.GenericViewSet):

    model = Applicant
    permission_classes = (IsAuthenticated, )
    serializers = {
        'default': OpportunityApplicantSerializer,
        'assign': AssignOpportunitySerializer,
        'reject': RejectOpportunitySerializer,
        'admin': OpportunityDetailSerializer,
        'sow': ApplicantEditSowSerializer,
        'update_sow': RequesterEditSowSerializer,
        'init_sow': InitialApplicantSowSerializer,
        'give_feedback': FeedbackApplicantSerializer,
    }

    def get_queryset(self):
        return self.model.objects.all()

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ValidationError:
            exc = exceptions.PermissionDenied()
            response = self.handle_exception(exc)
            self.response = self.finalize_response(
                request, response, *args, **kwargs)
            return self.response

    @action(detail=True, methods=['put'])
    def assign(self, request, pk):
        applicant = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=request.user,
            applicant=applicant,
        )
        serializer = self.serializers.get('admin')(
            instance=applicant.opportunity,
            context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def reject(self, request, pk):
        applicant = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=request.user,
            applicant=applicant,
        )
        serializer = self.serializers.get('admin')(
            instance=applicant.opportunity,
            context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_name='detail-sow', url_path='detail-sow')
    def sow(self, request, pk):
        applicant = self.get_object()
        sow = applicant.sow
        serializer = self.get_serializer(instance=sow)
        return Response(serializer.data)

    @sow.mapping.put
    def update_sow(self, request, pk):
        applicant = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=applicant)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=request.user,
            applicant=applicant,
        )
        return Response()

    @action(detail=True, methods=['get'], url_name='init-sow', url_path='init-sow')
    def init_sow(self, request, pk):
        applicant = self.get_object()
        sow_data = init_sow_from_applicant(applicant)
        serializer = self.get_serializer(sow_data)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def give_feedback(self, request, pk):
        applicant = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user_from=request.user,
            applicant=applicant,
        )
        context = self.get_serializer_context()
        context['action'] = 'admin'
        serializer = self.serializers.get('admin')(
            instance=applicant.opportunity,
            context=context)
        return Response(serializer.data)
