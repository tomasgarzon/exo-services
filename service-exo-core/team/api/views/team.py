from rest_framework import generics

from project.views.mixin import ProjectPermissionMixin
from utils.drf import SuccessMessageMixin

from ..serializers.team import TeamSerializer
from ...conf import settings
from ...models import Team


class TeamMixin(SuccessMessageMixin, ProjectPermissionMixin):
    serializer_class = TeamSerializer
    project_permission_required = settings.PROJECT_PERMS_CRUD_TEAM

    def get_queryset(self):
        return Team.objects.filter_by_project(self.get_project())


class TeamCreateView(TeamMixin, generics.CreateAPIView):
    success_message = '%(name)s was created successfully'
    swagger_schema = None

    def perform_create(self, serializer):
        serializer.save(project=self.get_project(), user_from=self.request.user)
        self.set_success_message(serializer.data)


class TeamUpdateView(TeamMixin, generics.RetrieveUpdateAPIView):
    success_message = '%(name)s was updated successfully'
    swagger_schema = None

    def perform_update(self, serializer):
        serializer.save(project=self.get_project(), user_from=self.request.user)
        self.set_success_message(serializer.data)
