from rest_framework import mixins, viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import get_user_model

from consultant.models import Consultant, ContractingData
from utils.drf.authentication import UsernameAuthentication

from ..serializers.external_user import UserSerializer
from ..serializers.contracting_data import ContractingDataSerializer


class UserViewSet(
        mixins.ListModelMixin, viewsets.GenericViewSet):
    model = get_user_model()
    authentication_classes = (UsernameAuthentication, )
    permission_classes = (IsAuthenticated,)
    queryset = get_user_model().objects.all()
    lookup_field = 'uuid'
    lookup_url_kwarg = 'uuid'
    serializers = {
        'default': UserSerializer,
        'contracting_data': ContractingDataSerializer,
        'update_contracting_data': ContractingDataSerializer,
    }
    filter_backends = [filters.SearchFilter]
    search_fields = ['emailaddress__email', 'email']

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    @action(detail=False, methods=['GET'], url_name='can-receive-opportunities', url_path='can-receive-opportunities')
    def can_receive_opportunities(self, request):
        queryset = Consultant.objects.filter_by_config_param('new_open_opportunity').users().actives_only()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='contracting-data', url_name='contracting-data')
    def contracting_data(self, request, uuid):
        user = self.get_object()
        try:
            contracting_data = user.consultant.exo_profile.contracting_data
        except ContractingData.DoesNotExist:
            contracting_data = ContractingData.objects.create(
                profile=user.consultant.exo_profile)
        serializer = self.get_serializer(contracting_data)
        return Response(serializer.data)

    @contracting_data.mapping.put
    def update_contracting_data(self, request, uuid):
        user = self.get_object()
        contracting_data = user.consultant.exo_profile.contracting_data
        serializer = self.get_serializer(contracting_data, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
