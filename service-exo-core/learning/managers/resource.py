from django.db import models

from ..querysets.resource import ResourceQuerySet


class ResourceManager(models.Manager):
    queryset_class = ResourceQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def actives(self):
        return self.get_queryset().actives()
