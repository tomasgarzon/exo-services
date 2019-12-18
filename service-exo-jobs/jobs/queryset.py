from django.db import models

from .conf import settings


class JobQuerySet(models.QuerySet):

    def filter_by_user(self, user):
        return self.filter(user=user)

    def filter_by_category(self, category):
        return self.filter(category=category)

    def filter_by_role(self, role):
        return self.filter(exo_role=role)

    def annotate_status_order(self):
        cases = [
            models.When(status=status, then=models.Value(index))
            for index, (status, _) in enumerate(settings.JOBS_STATUS_CHOICES)
        ]

        return self.annotate(
            status_order=models.Case(
                *cases,
                default=models.Value(5),
                output_field=models.IntegerField()))
