from django.db import models

from ..querysets.sprint_automated import SprintAutomatedQueryset


class SprintAutomatedManager(models.Manager):
    use_for_related_fields = True
    queryset_class = SprintAutomatedQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)
