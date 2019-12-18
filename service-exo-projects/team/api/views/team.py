from django.shortcuts import get_object_or_404

import reversion
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from project.models import Project

from ...models import Team
from ..serializers import team, team_role


class TeamViewSet(
        viewsets.ModelViewSet):

    model = Team
    permission_classes = (IsAuthenticated,)
    serializers = {
        'default': team.TeamSerializer,
        'create': team.TeamCreateSerializer,
        'update': team.TeamCreateSerializer,
        'add_user_role': team_role.UserTeamRoleCreateSerializer,
        'assign_project_roles': team_role.AssignProjectRolesToTeamSerializer,
        'move': team_role.UserMoveTeamSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

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

    @property
    def team(self):
        return self.get_object()

    def update(self, *args, **kwargs):
        with reversion.create_revision():
            response = super().update(*args, **kwargs)
            reversion.set_user(self.request.user)
            reversion.set_comment("Update from API")
            return response

    @action(detail=True, methods=['post'], url_name='add-user', url_path='add-user')
    def add_user_role(self, request, project_pk, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user_project_role = serializer.save(team=self.get_object())
        output_serializer = team_role.UserTeamRoleSerializer(
            new_user_project_role,
            context=self.get_serializer_context())
        return Response(output_serializer.data)

    @action(detail=True, methods=['post'], url_name='assign-users', url_path='assign-users')
    def assign_project_roles(self, request, project_pk, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = team.TeamSerializer(
            self.team,
            context=self.get_serializer_context())
        return Response(output_serializer.data)

    @action(detail=True, methods=['delete'], url_name='detail-user', url_path='user/(?P<user_team_role_pk>\\d+)')
    def delete_user_role(self, request, project_pk, pk, user_team_role_pk):
        team = self.get_object()
        user_team_role = team.user_team_roles.filter(pk=user_team_role_pk).first()
        user_team_role.delete()
        output_serializer = self.serializers.get('default')(
            team,
            context=self.get_serializer_context())
        return Response(output_serializer.data)

    @action(detail=True, methods=['put'], url_name='move-user', url_path='move-user/(?P<user_team_role_pk>\\d+)')
    def move(self, request, project_pk, pk, user_team_role_pk):
        team = self.get_object()
        user_team_role = team.user_team_roles.filter(pk=user_team_role_pk).first()
        serializer = self.get_serializer(user_team_role, data=request.data)
        serializer.is_valid(raise_exception=True)
        new_user_team_role = serializer.save(team=team)
        serializer = self.serializers.get('default')(
            Team.objects.filter(id__in=[pk, new_user_team_role.team.pk]),
            many=True,
            context=self.get_serializer_context())
        return Response(serializer.data)
