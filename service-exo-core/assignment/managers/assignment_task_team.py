from django.db import models

from ..queryset.assignment_task_team import AssignmentTaskTeamQuerySet


class AssignmentTaskTeamManager(models.Manager):
    queryset_class = AssignmentTaskTeamQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_team(self, team):
        return self.get_queryset().filter_by_team(team)

    def filter_by_task_item(self, task_item):
        return self.get_queryset().filter_by_task_item(task_item)
