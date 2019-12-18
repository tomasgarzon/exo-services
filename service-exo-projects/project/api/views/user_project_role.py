from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import viewsets, mixins, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import UserProjectRole, Project
from ..serializers import (
    user_project_role, user_project_role_create,
    user_project_role_update)
from ...tasks import MemberRemovedTask


class UserMixin:

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
                project_role__project_id=self.kwargs.get('project_pk'))
        else:
            queryset = self.model.objects.filter(
                project_role__project_id=self.kwargs.get('project_pk'),
                project_role__project__created_by=user)

        return queryset


class UsersViewSet(
        UserMixin,
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    serializers = {
        'default': user_project_role.UserProjectSerializer,
        'edit_exo_collaborator': user_project_role_update.ExOCollaboratorUpdateSerializer,
        'edit_participant': user_project_role_update.ParticipantUpdateSerializer,
        'edit_participant_teams': user_project_role_update.ParticipantTeamsUpdateSerializer,

    }
    lookup_field = 'uuid'
    model = get_user_model()
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter]
    search_fields = [
        'user_project_roles__project_role__exo_role__name',
        'user_team_roles__team_role__role',
        'user_team_roles__team__name']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = self.model.objects.filter(
                user_project_roles__project_role__project=self.project)
        else:
            queryset = self.model.objects.filter(
                user_project_roles__project_role__project=self.project,
                user_project_roles__project_role__project__created_by=user)
        return queryset.distinct()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        roles = UserProjectRole.objects.filter(
            user=user, project_role__project=self.project)
        previous_roles = list(roles.values_list('project_role__exo_role__name', flat=True))
        previous_roles = ', '.join(previous_roles)
        for user_role in roles:
            user_role.delete()
        if not self.project.is_draft:
            MemberRemovedTask().s(
                roles=previous_roles,
                user_id=user.id,
                project_id=self.project.id).apply_async()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_name='no-team', url_path='no-team')
    def users_without_team(self, request, project_pk):
        user = self.request.user

        if user.is_superuser:
            q1 = Q(user_project_roles__project_role__project_id=self.kwargs.get('project_pk'))
        else:
            q1 = Q(
                user_project_roles__project_role__project_id=self.kwargs.get('project_pk'),
                user_project_roles__project_role__project__created_by=user)

        COACH_OR_PARTICIPANT = [
            settings.EXO_ROLE_CODE_SPRINT_COACH,
            settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        ]
        q2 = Q(
            user_project_roles__project_role__exo_role__code__in=COACH_OR_PARTICIPANT)
        q3 = Q(
            user_team_roles__team__project_id=project_pk)
        queryset = self.model.objects.filter(q1 & q2).exclude(q3)
        search = request.GET.get('search')
        if search:
            queryset = queryset.filter(
                user_project_roles__project_role__exo_role__name__icontains=search)
        serializer = user_project_role.UserNoTeamProjectSerializer(
            queryset,
            many=True,
            context=self.get_serializer_context())
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_name='edit-exo-collaborator', url_path='edit-exo-collaborator')
    def edit_exo_collaborator(self, request, project_pk, uuid):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = self.serializers.get('default')(
            user,
            context=self.get_serializer_context())
        return Response(output_serializer.data)

    @action(detail=True, methods=['put'], url_name='edit-participant', url_path='edit-participant')
    def edit_participant(self, request, project_pk, uuid):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = self.serializers.get('default')(
            user,
            context=self.get_serializer_context())
        return Response(output_serializer.data)

    @action(detail=True, methods=['put'], url_name='edit-participant-teams', url_path='edit-participant-teams')
    def edit_participant_teams(self, request, project_pk, uuid):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        output_serializer = self.serializers.get('default')(
            user,
            context=self.get_serializer_context())
        return Response(output_serializer.data)


class UserProjectRoleViewSet(
        UserMixin,
        viewsets.ModelViewSet):

    model = UserProjectRole
    permission_classes = (IsAuthenticated,)


class ExOCollaboratorsViewSet(UserProjectRoleViewSet):

    serializers = {
        'default': user_project_role.ExOCollaboratorSerializer,
        'create': user_project_role_create.ExOCollaboratorCreateSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(project_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)


class ParticipantsViewSet(UserProjectRoleViewSet):

    serializers = {
        'default': user_project_role.ParticipantSerializer,
        'create': user_project_role_create.ParticipantCreateSerializer,
        'upload_csv': user_project_role_create.ParticipantCSVCreateSerializer,
        'parse_upload_csv': user_project_role_create.ParticipantCSVParseFileSerializer,
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(project_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)

    @action(detail=False, methods=['post'], url_name='upload-user', url_path='upload-user')
    def upload_csv(self, request, project_pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_project_roles = serializer.save()
        output_serializer = self.get_serializer(
            user_project_roles,
            many=True,
            context=self.get_serializer_context())
        return Response(output_serializer.data)

    @action(detail=False, methods=['post'], url_name='parse-upload-user', url_path='parse-upload-user')
    def parse_upload_csv(self, request, project_pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
