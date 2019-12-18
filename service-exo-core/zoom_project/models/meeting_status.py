from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..manager import ZoomMeetingStatusManager


class ZoomMeetingStatus(TimeStampedModel):
    meeting_id = models.CharField(max_length=20)
    meeting_uuid = models.CharField(max_length=50)
    status = models.CharField(
        max_length=10,
        choices=settings.ZOOM_PROJECT_MEETING_STATUS,
        null=True, blank=True,
    )
    host_id = models.CharField(
        max_length=50,
        null=True, blank=True,
    )
    objects = ZoomMeetingStatusManager()

    def __str__(self):
        return '{} {} {}'.format(
            self.meeting_id,
            self.meeting_uuid,
            self.status,
        )

    def is_started(self):
        return self.status == settings.ZOOM_PROJECT_CH_STARTED

    def is_ended(self):
        return self.status == settings.ZOOM_PROJECT_CH_ENDED
