import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

from model_utils.models import TimeStampedModel

from .conf import settings
from .manager import JobManager


class Job(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4)
    related_uuid = models.UUIDField(
        blank=True, null=True)
    related_class = models.CharField(
        max_length=2,
        choices=settings.JOBS_CLASS_CHOICES,
        blank=True, null=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='jobs',
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        'exo_role.Category',
        on_delete=models.CASCADE)
    exo_role = models.ForeignKey(
        'exo_role.ExORole',
        on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2,
        choices=settings.JOBS_STATUS_CHOICES,
        default=settings.JOBS_CH_STATUS_UNKNOWN,
    )
    status_detail = models.CharField(max_length=200, blank=True, null=True)

    title = models.CharField(max_length=400, blank=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    url = models.CharField(max_length=400, blank=True, null=True)
    extra_data = JSONField(blank=True, null=True)
    badge = models.BooleanField(default=True)

    objects = JobManager()

    def __str__(self):
        return str(self.user)

    def set_status(self):
        now = timezone.now()

        if (self.start and self.end) and self.start <= now <= self.end:
            if self.category.code == settings.EXO_ROLE_CATEGORY_SWARM:
                status = settings.JOBS_CH_STATUS_LIVE
            else:
                status = settings.JOBS_CH_STATUS_RUNNING

        elif self.start and self.start > now:
            status = settings.JOBS_CH_STATUS_UNSTARTED
        elif self.end and self.end < now:
            status = settings.JOBS_CH_STATUS_FINISHED
        else:
            status = settings.JOBS_CH_STATUS_UNKNOWN

        self.status = status
        self.save(update_fields=['status'])
