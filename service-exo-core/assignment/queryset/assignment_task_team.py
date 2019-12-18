from django.db import models


class AssignmentTaskTeamQuerySet(models.QuerySet):

    def filter_by_team(self, team):
        return self.filter(assignment_step_team__team=team)

    def filter_by_task_item(self, task_item):
        return self.filter(assignment_task_item=task_item)
