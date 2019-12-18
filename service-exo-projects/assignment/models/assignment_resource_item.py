from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from ..conf import settings


class AssignmentResourceItem(CreatedByMixin, TimeStampedModel):
    assignment_resource = models.ForeignKey(
        'AssignmentResource',
        related_name='assignment_resource_items',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    type = models.CharField(
        max_length=1,
        choices=settings.ASSIGNMENT_CH_RESOURCE_ITEM_TYPE,
        default=settings.ASSIGNMENT_CH_RESOURCE_ITEM_TYPE_DEFAULT)
    status = models.CharField(
        max_length=1,
        choices=settings.ASSIGNMENT_CH_RESOURCE_ITEM_STATUS,
        default=settings.ASSIGNMENT_CH_RESOURCE_ITEM_STATUS_DEFAULT)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.URLField(blank=True, null=True)
    iframe = models.TextField(blank=True, null=True)
    link = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.link
