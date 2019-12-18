from django.contrib.auth import get_user_model

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from forum.api.serializers.author import ForumAuthorSerializer
from project.views.mixin import SprintAutomatedProjectTeamPermission

from .mixins import QASessionGenericViewMixin
from ..serializers.qa_session_rest import QASessionTeamSerializer
from ...models import QASessionTeam


class QASessionTeamViewSet(
        SprintAutomatedProjectTeamPermission,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        QASessionGenericViewMixin):
    queryset = QASessionTeam.objects.all()

    serializers = {
        'default': QASessionTeamSerializer,
        'get_advisor_list': ForumAuthorSerializer,
    }

    def get_queryset(self):
        return self.queryset.filter(team=self.get_team())

    @action(detail=True, methods=['get'], url_path='advisors', url_name='advisors')
    def get_advisor_list(self, request, project_id, team_id, pk):
        instance = self.get_object()
        adv_list = instance.session.members.all().values_list('consultant__user', flat=True)
        serializer = self.get_serializer(
            get_user_model().objects.filter(pk__in=adv_list),
            many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='mentions', url_name='mentions')
    def get_mentions(self, request, project_id, team_id, pk):
        search = self.request.GET.get('search', None)
        user = self.request.user
        instance = self.get_object()
        data = list(filter(
            lambda p: user.pk != p.pk,
            instance.get_available_users(search=search, limit=10)
        ))
        serializer = ForumAuthorSerializer(data[:5], many=True)
        return Response(serializer.data, status.HTTP_200_OK)
