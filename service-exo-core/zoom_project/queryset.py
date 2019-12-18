from django.db import models

from .conf import settings


class ZoomMeetingStatusQuerySet(models.QuerySet):
    def actives(self):
        return self.filter(status=settings.ZOOM_PROJECT_CH_STARTED)

    def filter_by_meeting_id(self, meeting_id):
        return self.filter(meeting_id=meeting_id)
