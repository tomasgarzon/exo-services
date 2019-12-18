from django.db import models

from .queryset import PartnerQuerySet


class PartnerManager(models.Manager):

    queryset_class = PartnerQuerySet

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)
