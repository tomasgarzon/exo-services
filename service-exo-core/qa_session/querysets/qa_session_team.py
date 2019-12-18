from django.db import models


class QASessionTeamQueryset(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(session_project=project)

    def filter_by_datetime(self, when):
        return self.filter(
            session__start_at__lte=when,
            session__end_at__gte=when)

    def filter_next(self, when):
        return self.filter(
            session__start_at__gte=when).order_by('session__start_at')

    def filter_prev(self, when):
        return self.filter(
            session__end_at__lte=when).order_by('-session__end_at')
