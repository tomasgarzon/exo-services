from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from model_utils.models import TimeStampedModel

from .manager import CoreJobManager


class CoreJob(TimeStampedModel):
    uuid = models.UUIDField(
        blank=True, null=True)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True, null=True)
    object_id = models.PositiveIntegerField(
        blank=True, null=True)
    content_object = GenericForeignKey(
        'content_type', 'object_id')

    objects = CoreJobManager()

    def __str__(self):
        return '{} - {}'.format(self.uuid, self.content_object)

    def set_uuid(self, uuid):
        self.uuid = uuid
        self.save(update_fields=['uuid'])
