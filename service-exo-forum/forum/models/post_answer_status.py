from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin

from ..conf import settings


class PostAnswerStatus(ChoicesDescriptorMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
    )
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    status = models.CharField(
        max_length=1,
        choices=settings.FORUM_CH_POST_STATUS,
        default=settings.FORUM_CH_POST_STATUS_DEFAULT,
    )
    description = models.TextField(
        blank=True, null=True,
    )

    def __str__(self):
        return '{} - {} - {}'.format(
            self.content_object,
            self.user,
            self.status,
        )
