from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from utils.drf.authentication import UsernameAuthentication

from ...models import OpportunityGroup
from ..serializers.group import OpportunityGroupSerializer


class OpportunityGroupViewSet(
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    model = OpportunityGroup
    serializer_class = OpportunityGroupSerializer
    authentication_classes = (UsernameAuthentication, )
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['related_uuid']
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.model.objects.all()


class OpportunityGroupUserViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    model = OpportunityGroup
    serializer_class = OpportunityGroupSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['related_uuid']
    permission_classes = (IsAuthenticated,)
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.model.objects.all()
