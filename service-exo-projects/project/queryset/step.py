from django.db import models


class StepQuerySet(models.QuerySet):

    def filter_by_project(self, project):
        return self.filter(project=project)

    def filter_by_index_range(self, start, end):
        return self.filter(index__gte=start, index__lte=end)
