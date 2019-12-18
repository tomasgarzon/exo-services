from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import ProjectRole, Project
from ..serializers.project_role import ProjectCreateRoleSerializer


class ProjectRoleViewSet(
        viewsets.ModelViewSet):

    model = ProjectRole
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectCreateRoleSerializer
    pagination_class = None

    @property
    def project(self):
        return get_object_or_404(Project, pk=self.kwargs.get('project_pk'))

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            queryset = self.model.objects.filter(
                project_id=self.kwargs.get('project_pk'))
        else:
            queryset = self.model.objects.filter(
                project_id=self.kwargs.get('project_pk'),
                project__created_by=user)

        return queryset
