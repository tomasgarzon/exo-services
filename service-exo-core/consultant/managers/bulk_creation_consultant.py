from django.db import models

from ..querysets.bulk_creation_consultant import BulkCreationConsultantQueryset


class BulkCreationConsultantManager(models.Manager):
    use_for_related_fields = True
    queryset_class = BulkCreationConsultantQueryset

    def get_queryset(self):
        return self.queryset_class(
            self.model,
            using=self._db,
        )

    def success(self):
        return self.get_queryset().filter(status=self.model.SUCCESS_MESSAGE)
