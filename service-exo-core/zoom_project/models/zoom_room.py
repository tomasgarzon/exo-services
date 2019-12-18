from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel


class ZoomRoom(TimeStampedModel):
    """
        Object Zoom Room is available to relate with any kind of
        object like Teams
    """

    _zoom_settings = models.ForeignKey(
        'zoom_project.ZoomSettings',
        related_name='rooms',
        on_delete=models.CASCADE,
    )

    # Any object that can use ZoomRooms
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    meeting_id = models.CharField(
        'Meeting ID (Zoom)',
        null=True, blank=True,
        max_length=256,
    )
    host_meeting_id = models.TextField(
        'Host Meeting ID (Zoom)',
        null=True, blank=True,
    )
    zoom_id = models.CharField(
        'Internal Meeting ID (Zoom)',
        null=True, blank=True,
        max_length=256,
    )

    class Meta:
        verbose_name_plural = 'Zoom Rooms'
        verbose_name = 'Zoom Room'
        app_label = 'zoom_project'

    @property
    def meeting_object(self):
        """
        Object that owns the Room
        """
        return self.content_object

    @property
    def zoom_settings(self):
        return self.meeting_object.settings

    def update_host_meeting_id(self):
        """
            Should be called by celery
        """
        self.host_meeting_id = self.zoom_settings.get_meeting_token(
            self.meeting_id)
        self.save(update_fields=['host_meeting_id'])

    def schedule_meeting(self, title, start, timezone, duration):
        response = self.zoom_settings.get_schedule_meeting(
            self.meeting_id, title, start, timezone, duration)
        if response is not None:
            self.host_meeting_id = response['start_url']
            self.zoom_id = response['id']
            self.save(update_fields=['zoom_id', 'host_meeting_id'])
