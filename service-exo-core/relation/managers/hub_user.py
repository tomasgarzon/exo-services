from django.db import models

from ..queryset.hub_user import HubUserQuerySet


class HubUserManager(models.Manager):
    queryset_class = HubUserQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def exclude_consulting(self):
        return self.get_queryset().exclude_consulting()
