from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from assignment.api.serializers.assignment_task_item import AssignmentTaskItemListStatusSerializer
from assignment.api.serializers.assignment_task_item import AssignmentTaskItemSerializer
from project.api.serializers.step_rating import (
    StepRatingSerializer,
    RatingSerializer)
from utils.permissions.objects_project import get_project_for_user
from utils.permissions.objects import get_team_for_user

from ..serializers.step import StepDetailSerializer, StepSerializer
from ...models import Step
from ...conf import settings


class StepViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    queryset = Step.objects.all()
    permission_classes = (IsAuthenticated,)
    serializers = {
        'default': StepSerializer,
        'retrieve': StepDetailSerializer,
        'tasks_done': AssignmentTaskItemListStatusSerializer,
        'tasks_undone': AssignmentTaskItemListStatusSerializer,
        'feedback': StepRatingSerializer,
    }

    @property
    def project(self):
        return get_object_or_404(
            get_project_for_user(self.request.user),
            pk=self.kwargs.get('project_pk'))

    @property
    def team(self):
        return get_object_or_404(
            get_team_for_user(self.project, self.request.user),
            pk=self.kwargs.get('team_pk'))

    def get_queryset(self):
        return self.queryset.filter_by_project(self.project)

    def get_serializer_class(self):
        return self.serializers.get(
            self.action,
            self.serializers['default'],
        )

    def get_tasks_serializer(self, tasks_items):
        return AssignmentTaskItemSerializer(tasks_items, many=True, context={'view': self})

    @action(detail=True, methods=['post'], url_path='tasks-done')
    def tasks_done(self, request, project_pk, team_pk, pk):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tasks_items = serializer.save(
            step=instance,
            user_from=request.user,
            team=self.team,
            new_status=settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_DONE)
        serializer_tasks = self.get_tasks_serializer(tasks_items)
        return Response(serializer_tasks.data)

    @action(detail=True, methods=['post'], url_path='tasks-undone')
    def tasks_undone(self, request, project_pk, team_pk, pk):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tasks_items = serializer.save(
            step=instance,
            user_from=request.user,
            team=self.team,
            new_status=settings.ASSIGNMENT_TASK_TEAM_CH_STATUS_TO_DO)
        serializer_tasks = self.get_tasks_serializer(tasks_items)
        return Response(serializer_tasks.data)

    @action(detail=True, methods=['post'], url_path='feedback')
    def feedback(self, request, project_pk, team_pk, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.save(
            user_from=request.user,
        )
        serializer_rating = RatingSerializer(rating)
        return Response(serializer_rating.data)

    @action(detail=True, methods=['get'], url_path='download-report')
    def download_report(self, request, project_pk, team_pk, pk):
        instance = self.get_object()
        instance.can_download_report(
            request.user,
            raise_exceptions=True)

        xlsx_wrapper = instance.create_feedbacks_excel_report()
        response = HttpResponse(
            xlsx_wrapper.read(),
            content_type=xlsx_wrapper.content_type,
        )
        response['Content-Disposition'] = xlsx_wrapper.content_disposition
        return response
