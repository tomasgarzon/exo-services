from django.conf import settings

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from project.views.mixin import ProjectPermissionMixin
from utils.drf import SuccessMessageMixin
from project.certification_helpers import CertificationProjectWrapper

from ...serializers.project.user_role import (
    UserProjectRoleSerializer, UploadUserProjectRoleSerializer)
from ....models import UserProjectRole


class UserProjectRoleViewSet(
        ProjectPermissionMixin,
        SuccessMessageMixin,
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        viewsets.GenericViewSet
):

    model = UserProjectRole
    serializer_class = UserProjectRoleSerializer
    success_message = '%(name)s was created successfully'
    queryset = UserProjectRole.objects.all()
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGER
    swagger_schema = None

    def get_queryset(self):
        return self.get_project().users_roles.all()

    def perform_create(self, serializer):
        serializer.save(
            user_from=self.request.user,
            project=self.get_project(),
        )
        self.set_success_message({'name': serializer.instance.user.get_full_name()})

    def perform_update(self, serializer):
        serializer.save(
            user_from=self.request.user,
            project=self.get_project(),
        )

    def perform_destroy(self, instance):
        project = self.get_project()
        project.check_edit_perms(self.request.user)
        instance.delete()
        self.set_message('%(user)s as %(role)s was removed successfully ' % {
            'user': instance.user, 'role': instance.exo_role.name,
        })

    @action(detail=False, methods=['post'], url_path='upload', url_name='upload')
    def upload(self, request, project_id):
        project = self.get_project()
        serializer = UploadUserProjectRoleSerializer(
            data=request.data,
            context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        users = serializer.save(user_from=request.user, project=project)
        new_serializer = UserProjectRoleSerializer(
            users,
            many=True)
        return Response(new_serializer.data)

    @action(detail=True, methods=['post'], url_path='generate-certificate', url_name='generate-certificate')
    def generate_certificate(self, request, project_id, pk):
        instance = self.get_object()
        certification_wrapper = CertificationProjectWrapper(instance.project)
        certification_wrapper.release_simple_credential(request.user, instance)
        return Response()

    @action(detail=False, methods=['post'], url_path='send-certificates', url_name='send-certificates')
    def send_certificates(self, request, project_id):
        project = self.get_project()
        certification_wrapper = CertificationProjectWrapper(project)
        certification_wrapper.release_group_credential(request.user, project)
        return Response()

    @action(detail=False, methods=['post'], url_path='send-certificates-feedback')
    def send_certificates_feedback(self, request, project_id):
        # TODO next week
        return Response()
