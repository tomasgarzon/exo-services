import uuid

from django.db import models

from model_utils.models import TimeStampedModel

from job.mixins import JobMixin
from utils.models import CreatedByMixin

from ..managers.qa_session import QASessionManager
from ..conf import settings
from .mails import QASessionMailMixin


class QASession(QASessionMailMixin, JobMixin, CreatedByMixin, TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200, default='Swarm Session')
    project = models.ForeignKey(
        'project.Project',
        related_name='qa_sessions',
        on_delete=models.CASCADE)
    advisors = models.ManyToManyField(
        'relation.ConsultantProjectRole',
        related_name='qa_sessions_advisors')
    members = models.ManyToManyField(
        'relation.ConsultantProjectRole',
        through='QASessionAdvisor',
        related_name='qa_sessions')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    objects = QASessionManager()

    class Meta:
        ordering = ['start_at']

    def __str__(self):
        return '{} {}: {} - {}'.format(
            self.name, self.project, self.start_at, self.end_at)

    def get_available_users(self, search, limit=0):
        head_coach = self.project.project_manager
        participants = [head_coach.user] if head_coach else []
        participants += [_.consultant.user for _ in self.members.all()]
        participants = list(set(participants))
        if search:
            search = search.lower()
            participants = list(filter(
                lambda p: search in p.full_name.lower(), participants))
        participants.sort(key=lambda p: p.full_name.lower())

        if limit:
            return participants[0:limit]
        return participants

    @property
    def normalized_start_at(self):
        timezone = self.project.timezone
        return timezone.normalize(self.start_at)

    @property
    def normalized_end_at(self):
        timezone = self.project.timezone
        return timezone.normalize(self.end_at)

    @property
    def url(self):
        return settings.FRONTEND_JOBS_SWARM_PAGE.format(**{'pk': self.pk})
