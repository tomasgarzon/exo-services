from django.db import models

from .queryset import ZoomMeetingStatusQuerySet


class ZoomMeetingStatusManager(models.Manager):
    use_for_related_fields = True
    use_in_migrations = True
    queryset_class = ZoomMeetingStatusQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_team(self, team):
        return self.get_queryset().filter_by_meeting_id(team.zoom_id)
