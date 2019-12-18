from django.db import models

from ..queryset.information_block import InformationBlockQuerySet


class InformationBlockManager(models.Manager):
    queryset_class = InformationBlockQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_type(self, type):
        return self.get_queryset().filter_by_type(type)
