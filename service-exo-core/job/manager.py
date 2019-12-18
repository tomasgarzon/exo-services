from django.db import models
from django.contrib.contenttypes.models import ContentType

from .queryset import CoreJobQuerySet


class CoreJobManager(models.Manager):
    queryset_class = CoreJobQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def create_from_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        self.get_queryset().filter_by_instance(instance).delete()
        return super().create(content_type=content_type, object_id=instance.pk)
