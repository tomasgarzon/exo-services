from django.shortcuts import get_object_or_404

from rest_framework import viewsets, exceptions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from opportunities.helper import initialize_advisor_request_settings_for_project
from opportunities.serializers.advisor_request_settings import AdvisorRequestSettingsSerializer

from ...exceptions import ProjectRemovedException
from ...models import Project
from ..serializers.project_basic import (
    ProjectBasicInfoSerializer,
    ProjectListSerializer)
from ..serializers.cancelation import CancelationSerializer
from ..serializers.project_settings import ProjectSettingsSerializer
from ..serializers.project_launch import ProjectLaunchSerializer


class ProjectViewSet(
        viewsets.ModelViewSet):

    model = Project
    permission_classes = (IsAuthenticated,)
    serializers = {
        'default': ProjectBasicInfoSerializer,
        'list': ProjectListSerializer,
        'retrieve': ProjectListSerializer,
        'destroy': CancelationSerializer,
        'edit_settings': ProjectSettingsSerializer,
        'update_settings': ProjectSettingsSerializer,
        'launch': ProjectLaunchSerializer,
        'see_advisor_request_settings': AdvisorRequestSettingsSerializer,
        'update_advisor_request_settings': AdvisorRequestSettingsSerializer,
    }
    page_size = 10
    page_size_query_param = 'page_size'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['start', 'status_order']
    ordering = ['-start', 'status_order']

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except ValidationError:
            exc = exceptions.PermissionDenied()
            response = self.handle_exception(exc)
            self.response = self.finalize_response(
                request, response, *args, **kwargs)
            return self.response
        except ProjectRemovedException as err:
            response = Response(
                data={
                    'classname': err.project.__class__.__name__,
                    'object_id': err.project.pk},
                content_type="application/json",
                status=status.HTTP_410_GONE)
            response.accepted_renderer = JSONRenderer()
            response.accepted_media_type = "application/json"
            response.renderer_context = {}
            return response

    def check_is_removed(self):
        if self.action == 'retrieve':
            project = get_object_or_404(self.model, pk=self.kwargs.get('pk'))
            if project.is_removed:
                raise ProjectRemovedException(project, 'Project removed')

    def get_queryset(self):
        self.check_is_removed()
        user = self.request.user

        if user.is_superuser:
            queryset = self.model.objects.all()
        else:
            queryset = self.model.objects.filter(created_by=user)

        queryset = queryset.not_removed().annotate_status_order()

        return queryset

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            self.get_object(), data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(instance, serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, serializer):
        instance.remove(
            self.request.user,
            comment=serializer.validated_data.get('comment'),
        )

    @action(detail=True, methods=['put'])
    def launch(self, request, pk):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.serializers.get('retrieve')(
            project,
            context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='settings', url_name='settings')
    def edit_settings(self, request, pk):
        project = self.get_object()
        serializer = self.get_serializer(project.settings)
        return Response(serializer.data)

    @edit_settings.mapping.put
    def update_settings(self, request, pk):
        project = self.get_object()
        serializer = self.get_serializer(project.settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.serializers.get('retrieve')(
            project,
            context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='advisor-request-settings', url_name='advisor-request-settings')
    def see_advisor_request_settings(self, request, pk):
        project = self.get_object()
        try:
            advisor_settings = project.advisor_request_settings
        except AttributeError:
            advisor_settings = initialize_advisor_request_settings_for_project(project, request.user)
        serializer = self.get_serializer(advisor_settings)
        return Response(serializer.data)

    @see_advisor_request_settings.mapping.put
    def update_advisor_request_settings(self, request, pk):
        project = self.get_object()
        try:
            advisor_request_settings = project.advisor_request_settings
        except AttributeError:
            advisor_request_settings = initialize_advisor_request_settings_for_project(project, request.user)
        serializer = self.get_serializer(
            advisor_request_settings, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
