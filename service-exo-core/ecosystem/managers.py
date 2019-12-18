from django.db import models

from .queryset import MemberQueryset


class MemberManager(models.Manager):
    queryset_class = MemberQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_for_public(self):
        return self.get_queryset().filter_for_public()
