from rest_framework import generics

from guardian.mixins import PermissionRequiredMixin as GuardianRequiredPermission

from utils.api.doc_mixin import APIObjectMixin

from ..serializers.project_status import ProjectChangeStatusSerializer
from ...conf import settings
from ...models import Project


class ProjectChangeStatusView(
        GuardianRequiredPermission,
        APIObjectMixin,
        generics.UpdateAPIView
):
    model = Project
    queryset = Project.objects.all()
    serializer_class = ProjectChangeStatusSerializer
    permission_required = settings.PROJECT_PERMS_EDIT_PROJECT
    return_404 = True
