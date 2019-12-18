from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from project.models import Project

from ...models import ProjectTeamRole
from ..serializers.role import TeamRoleSerializer


class TeamRoleViewSet(
        viewsets.ModelViewSet):

    model = ProjectTeamRole
    permission_classes = (IsAuthenticated,)
    serializer_class = TeamRoleSerializer
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
