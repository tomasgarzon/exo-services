from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from utils.drf.authentication import UsernameAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from utils.permissions.objects_project import get_project_for_user

from ...models import Project
from ..serializers import project_view


class ProjectRetrieveViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    model = Project
    permission_classes = (IsAuthenticated,)
    serializers = {
        'default': project_view.ViewProjectSerializer,
        'list': project_view.ViewZoneProjectSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_queryset(self):
        return get_project_for_user(self.request.user)

    @property
    def project(self):
        return self.get_object()


class ProjectRetrieveByUUIDViewSet(ProjectRetrieveViewSet):
    lookup_field = 'uuid'
    authentication_classes = (UsernameAuthentication, JSONWebTokenAuthentication)
    serializers = {
        'default': project_view.ViewZoneProjectSerializer,
        'list': project_view.ViewZoneProjectSerializer,
        'filter_by_team': project_view.ViewZoneProjectSerializer,
    }

    @action(detail=False, methods=['GET'])
    def filter_by_team(self, request):
        team_uuid = request.GET.get('team', None)
        if not team_uuid:
            queryset = self.model.objects.none()
        else:
            queryset = self.model.objects.filter(teams__uuid=team_uuid)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
