from django.db import models
from django.contrib.contenttypes.models import ContentType


class CoreJobQuerySet(models.QuerySet):

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        return self.filter(
            content_type=content_type,
            object_id=instance.pk,
        )
