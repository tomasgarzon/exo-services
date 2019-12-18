from django.db import models

from model_utils.models import TimeStampedModel

from utils.descriptors import ChoicesDescriptorMixin
from utils.collections import StatusString

from ..conf import settings


class OpportunityStatus(ChoicesDescriptorMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
    )
    opportunity = models.ForeignKey(
        'Opportunity',
        on_delete=models.CASCADE,
        related_name='history',
    )
    status = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_STATUS,
        default=settings.OPPORTUNITIES_CH_STATUS_DEFAULT,
    )
    description = models.TextField(
        blank=True, null=True,
    )

    def __str__(self):
        return '{} - {} - {}'.format(
            self.opportunity,
            self.user,
            self.status,
        )

    @property
    def _status(self):
        return StatusString(
            self.status,
            choices=settings.OPPORTUNITIES_CH_STATUS)
