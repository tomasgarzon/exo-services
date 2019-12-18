from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from utils.permissions.objects_project import get_project_for_user

from ..serializers import user_project_role


class UserViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = user_project_role.UserProjectSerializer

    @property
    def project(self):
        return get_object_or_404(
            get_project_for_user(self.request.user),
            pk=self.kwargs.get('project_pk'))

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        q1 = Q(
            user_project_roles__project_role__project_id=self.project.id,
            user_project_roles__project_role__exo_role__name__icontains=search
        )
        q2 = Q(
            user_project_roles__project_role__project_id=self.project.id,
            user_team_roles__team__project_id=self.project.id,
            user_team_roles__team_role__role__icontains=search
        )
        q3 = Q(
            user_project_roles__project_role__project_id=self.project.id,
            user_team_roles__team__project_id=self.project.id,
            user_team_roles__team__name__icontains=search
        )
        return self.queryset.filter(q1 | q2 | q3).distinct()
