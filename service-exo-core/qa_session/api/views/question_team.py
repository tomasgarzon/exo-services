from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from forum.api.serializers.author import ForumAuthorSerializer
from project.views.mixin import SprintAutomatedProjectTeamPermission

from .mixins import (
    QASessionGenericViewMixin,
    QASessionQuestionGenericMixin)
from ...models import QASessionTeam


class QASessionQuestionTeamViewSet(
        SprintAutomatedProjectTeamPermission,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        QASessionQuestionGenericMixin,
        QASessionGenericViewMixin):
    swagger_schema = None

    def get_queryset(self):
        qs = super().get_queryset()
        session = QASessionTeam.objects.filter(
            team=self.get_team()
        ).get(pk=self.kwargs['swarm_id'])
        return qs.filter(
            qa_sessions=session)

    def perform_destroy(self, instance):
        instance.mark_as_removed(self.request.user)
        return instance

    @action(detail=True, methods=['get'], url_path='mentions', url_name='mentions')
    def get_mentions(self, request, project_id, team_id, swarm_id, pk):
        search = self.request.GET.get('search', None)
        user = self.request.user
        instance = self.get_object()
        qa_team = instance.qa_sessions.get(
            team=instance.team)
        data = list(filter(
            lambda p: user.pk != p.pk,
            qa_team.get_available_users(search=search, limit=10)
        ))
        serializer = ForumAuthorSerializer(data[:5], many=True)
        return Response(serializer.data, status.HTTP_200_OK)
