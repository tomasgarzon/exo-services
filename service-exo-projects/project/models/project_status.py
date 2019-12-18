from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class ProjectStatus(CreatedByMixin, TimeStampedModel):
    project = models.ForeignKey(
        'Project',
        related_name='statuses',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=1,
        choices=settings.PROJECT_CH_STATUS,
        default=settings.PROJECT_CH_STATUS_DRAFT,
    )

    def __str__(self):
        return '{}-{}'.format(self.created_by, self.get_status_display())
