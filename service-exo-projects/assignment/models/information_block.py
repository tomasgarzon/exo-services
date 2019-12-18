from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin

from ..managers.information_block import InformationBlockManager
from ..conf import settings


class InformationBlock(CreatedByMixin, TimeStampedModel):
    limit = Q(app_label='assignment', model='AssignmentStep') | Q(app_label='assignment', model='AssignmentTaskItem')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        limit_choices_to=limit)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    title = models.CharField(max_length=200, blank=True, null=True)
    subtitle = models.CharField(max_length=400, blank=True, null=True)
    type = models.CharField(
        max_length=1,
        choices=settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPES,
        default=settings.ASSIGNMENT_INFORMATION_BLOCK_CH_TYPE_DEFAULT,
    )
    order = models.PositiveIntegerField(default=0)
    section = models.CharField(
        max_length=1,
        choices=settings.ASSIGNMENT_INFORMATION_BLOCK_CH_SECTIONS,
        default=settings.ASSIGNMENT_INFORMATION_BLOCK_CH_SECTION_DEFAULT)

    objects = InformationBlockManager()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return 'Object: {} - Type: {}'.format(self.content_object, self.get_type_display())
