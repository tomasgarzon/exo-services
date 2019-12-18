from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class UploadedFileVisibility(CreatedByMixin, TimeStampedModel):
    uploaded_file = models.ForeignKey('UploadedFile', related_name='visibility', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, blank=True, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    related = GenericForeignKey('content_type', 'object_id')
    visibility = models.CharField(
        max_length=1,
        choices=settings.FILES_VISIBILITY_CHOICES,
        default=settings.FILES_VISIBILITY_PRIVATE)

    def __str__(self):
        return self.uploaded_file.filename_sanitized
