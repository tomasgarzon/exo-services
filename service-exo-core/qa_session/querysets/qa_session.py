from django.db import models
from django.utils import timezone


class QASessionQueryset(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(project=project)

    def actives(self, now=None):
        if not now:
            now = timezone.now()
        return self.filter(
            start_at__lte=now,
            end_at__gte=now)

    def filter_by_advisor(self, consultant):
        return self.filter(members__consultant=consultant)
