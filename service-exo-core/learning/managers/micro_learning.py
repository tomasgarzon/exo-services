from django.db import models

from ..querysets.microlearning import MicrolearningQueryset


class MicroLearningManager(models.Manager):

    queryset_class = MicrolearningQueryset

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_step(self, step):
        return self.get_queryset().filter_by_step(step)
