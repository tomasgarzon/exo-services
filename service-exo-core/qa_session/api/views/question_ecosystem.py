from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from forum.api.serializers.author import ForumAuthorSerializer
from ..views.mixins import (
    QASessionGenericViewMixin,
    QASessionQuestionGenericMixin
)
from ...models import QASession


class QASessionQuestionEcosystemViewSet(
        QASessionQuestionGenericMixin,
        QASessionGenericViewMixin):

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        session = QASession.objects.all()
        if not user.is_superuser:
            session = QASession.objects.filter_by_advisor(
                self.request.user)
        session = session.get(pk=self.kwargs['swarm_id'])
        return qs.filter(qa_sessions__session=session)

    @action(detail=True, methods=['get'], url_path='mentions')
    def get_mentions(self, request, swarm_id, pk):
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
