from django.db import models

from ..queryset.assignment_step import AssignmentStepQuerySet


class AssignmentStepManager(models.Manager):
    queryset_class = AssignmentStepQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_step(self, step):
        return self.get_queryset().filter_by_step(step)

    def filter_by_stream(self, stream):
        return self.get_queryset().filter_by_stream(stream)

    def exclude_by_stream(self, stream):
        return self.get_queryset().exclude_by_stream(stream)
