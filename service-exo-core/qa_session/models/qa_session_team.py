from django.db import models
from django.db.models import Count, Avg
from django.contrib.contenttypes.fields import GenericRelation
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from ..managers.qa_session_team import QASessionTeamManager


class QASessionTeam(CreatedByMixin, TimeStampedModel):
    team = models.ForeignKey(
        'team.Team',
        related_name='qa_sessions',
        on_delete=models.CASCADE)
    session = models.ForeignKey(
        'QASession',
        related_name='teams',
        on_delete=models.CASCADE)
    questions = GenericRelation(
        'forum.Post',
        related_query_name='qa_sessions')

    objects = QASessionTeamManager()

    def __str__(self):
        return '{} - {}'.format(self.team, self.session)

    class Meta:
        ordering = ['session__start_at']

    @property
    def url(self):
        return settings.FRONTEND_PROJECT_PAGE.format(
            **{
                'project_id': self.session.project.pk,
                'team_id': self.team.pk,
                'section': 'swarm-session',
            })

    def total_answers_by_participant(self, user):
        return self.questions.filter(created_by=user).aggregate(total=Count('answers'))['total']

    @property
    def rating_average(self):
        return self.questions.aggregate(avg=Avg('answers__ratings__rating'))['avg']

    def get_available_users(self, search, limit=0):
        participants = list(
            self.team.get_granted_users())
        participants = participants + self.session.get_available_users(search)
        participants = list(set(participants))
        if search:
            search = search.lower()
            participants = list(filter(
                lambda p: search in p.full_name.lower(), participants))
        participants.sort(key=lambda p: p.full_name.lower())
        if limit:
            return participants[0:limit]
        return participants
