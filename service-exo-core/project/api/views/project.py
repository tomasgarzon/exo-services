from django.conf import settings

from rest_framework import viewsets, renderers, mixins, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from exo_role.models import ExORole
from utils.drf.parsers import CamelCaseJSONParser
from utils.drf.authentication import JSONWebTokenAuthentication, UsernameAuthentication
from permissions.shortcuts import has_project_perms

from ...models import Project
from ..serializers.project_list import (
    ProjectListSerializer,
    ProjectUpdateSerializer,
    ProjectRetrieveSerializer,
)
from ..serializers.project_settings import ProjectSettingsSerializer
from ..serializers.project_status import ProjectChangeStatusSerializer
from ..serializers.project import ProjectBackofficeSerializer


class ProjectViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet):

    model = Project
    permission_classes = (IsAuthenticated, )
    parser_classes = (CamelCaseJSONParser, MultiPartParser)
    renderer_classes = (CamelCaseJSONRenderer, renderers.JSONRenderer, )
    lookup_field = 'slug'

    serializers = {
        'default': ProjectListSerializer,
        'update': ProjectUpdateSerializer,
        'retrieve': ProjectRetrieveSerializer,
        'project_settings': ProjectSettingsSerializer,
        'change_status': ProjectChangeStatusSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_queryset(self):
        return self.model.objects.filter_by_user(
            self.request.user,
        ).order_by('-start')

    def perform_update(self, serializer):
        self.check_edit_permissions()
        serializer.save(
            user_from=self.request.user,
        )

    def check_edit_permissions(self):
        user = self.request.user
        project = self.get_object()
        valid = has_project_perms(
            project,
            settings.PROJECT_PERMS_EDIT_PROJECT,
            user)
        if not valid:
            raise exceptions.PermissionDenied

    @action(detail=True, methods=['PUT', 'GET'], url_path='settings', url_name='settings')
    def project_settings(self, request, slug):
        self.check_edit_permissions()
        project = self.get_object()

        if request.method == 'PUT':
            serializer = self.get_serializer(instance=project.settings, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:
            serializer = self.get_serializer(
                instance=project.settings,
            )
        return Response(serializer.data)

    @action(detail=True, methods=['PUT'], url_path='change-status')
    def change_status(self, request, slug):
        self.check_edit_permissions()
        project = self.get_object()
        serializer = self.get_serializer(instance=project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user_from=request.user)
        return Response(serializer.data)


class ProjectBackofficeViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    queryset = Project.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectBackofficeSerializer

    @action(detail=True, methods=['GET'], url_path='customize-roles')
    def customize_roles(self, request, pk):
        project = self.get_object()
        codes = dict(project.customize.get('roles').get('labels')).keys()
        exo_roles = ExORole.objects.filter(code__in=codes)
        serialize_data = []

        for exo_role in exo_roles:
            serialize_data.append({
                'pk': exo_role.pk,
                'code': exo_role.code,
                'name': '{} - {}'.format(exo_role.categories.first().name, exo_role.name)
            })

        return Response(serialize_data)


class ProjectByUUIDViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    queryset = Project.objects.all()
    model = Project
    permission_classes = (IsAuthenticated,)
    authentication_classes = (UsernameAuthentication, JSONWebTokenAuthentication)
    serializer_class = ProjectBackofficeSerializer
    lookup_field = 'uuid'
    renderer_classes = (CamelCaseJSONRenderer, renderers.JSONRenderer, )

    @action(detail=False, methods=['GET'])
    def filter_by_team(self, request):
        team_uuid = request.GET.get('team', None)
        if not team_uuid:
            queryset = self.model.objects.none()
        else:
            queryset = self.model.objects.filter(teams__uuid=team_uuid)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
