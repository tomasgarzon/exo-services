from django.db import models

from ..querysets.bulk_creation import BulkCreationQueryset


class BulkCreationManager(models.Manager):
    use_for_related_fields = True
    queryset_class = BulkCreationQueryset

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )
