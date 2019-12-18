from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.drf.authentication import UsernameAuthentication
from project.models import Project
from opportunities.serializers.user_from_opportunity import AddUserFromOpportunitySerializer


class ProjectOpportunityView(viewsets.GenericViewSet):
    serializer_class = AddUserFromOpportunitySerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (UsernameAuthentication, )
    model = Project
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.model.objects.all()

    @action(detail=True, methods=['post'])
    def add_from_opportunity(self, request, uuid):
        project = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response()
