from django.db import models
from django.db.models import Q


class AssignmentStepQuerySet(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(step__project=project)

    def filter_by_step(self, step):
        return self.filter(step=step)

    def filter_by_stream(self, stream):
        return self.filter(Q(streams=stream))

    def exclude_by_stream(self, stream):
        return self.exclude(Q(streams=stream))
