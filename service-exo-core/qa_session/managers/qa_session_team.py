from django.db import models
from django.utils import timezone

from ..querysets.qa_session_team import QASessionTeamQueryset


class QASessionTeamManager(models.Manager):

    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = QASessionTeamQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def select_session_by_datetime(self, when=None):
        if not when:
            when = timezone.now()
        happening_now = self.get_queryset().filter_by_datetime(when)
        if happening_now:
            return happening_now.first()
        next_session = self.get_queryset().filter_next(when)
        if next_session:
            return next_session.first()
        last_session = self.get_queryset().filter_prev(when)
        if last_session:
            return last_session.first()
        return None
