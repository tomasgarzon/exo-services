from django.conf import settings

from rest_framework import viewsets, mixins, serializers, renderers
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from project.views.mixin import ProjectPermissionMixin

from utils.drf import SuccessMessageMixin

from ...serializers.project.consultant_role import ConsultantProjectRoleSerializer
from ...serializers.project.consultant_project_role import ConsultantProjectRoleFullSerializer
from ....models import ConsultantProjectRole


class ConsultantProjectRoleViewSet(
        ProjectPermissionMixin,
        SuccessMessageMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
):

    model = ConsultantProjectRole
    success_message = '%(name)s was created successfully'
    project_permission_required = settings.PROJECT_PERMS_PROJECT_MANAGE_CONSULTANT
    renderer_classes = (
        CamelCaseJSONRenderer, renderers.JSONRenderer,)
    serializers = {
        'default': ConsultantProjectRoleSerializer,
        'list': ConsultantProjectRoleFullSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_queryset(self):
        return self.get_project().consultants_roles.all()

    def perform_create(self, serializer):
        serializer.save(user_from=self.request.user)
        self.set_success_message({'name': serializer.instance.consultant.user.get_full_name()})

    def perform_destroy(self, instance):
        project = self.get_project()
        project.check_edit_perms(self.request.user)
        if not instance.can_be_deleted:
            raise serializers.ValidationError('Coach must exist in the project')
        instance.delete()
        self.set_message('%(consultant)s as %(role)s was removed successfully ' % {
            'consultant': instance.consultant, 'role': instance.exo_role.name,
        })
