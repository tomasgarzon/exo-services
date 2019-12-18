from django.db import models

from .queryset import JobQuerySet


class JobManager(models.Manager):
    queryset_class = JobQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_category(self, category):
        return self.get_queryset().filter_by_category(category)
