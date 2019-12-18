from django.db import models
from django.contrib.contenttypes.models import ContentType
from model_utils.models import TimeStampedModel

from .zoom_room import ZoomRoom
from ..helpers import ZoomUsHelper
from ..conf import settings


class ZoomSettings(
    TimeStampedModel,
    ZoomUsHelper
):

    zoom_api_key = models.CharField(max_length=256)
    zoom_secret_key = models.CharField(max_length=256)

    project = models.OneToOneField(
        'project.Project',
        blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='zoom_settings',
    )

    class Meta:
        verbose_name_plural = 'Zooms Settings'
        verbose_name = 'Zoom Settings'

    def __str__(self):
        return 'Zoom Settings - {}'.format(self.project)

    @property
    def is_default(self):
        return self.zoom_api_key == settings.ZOOM_PROJECT_API_KEY and \
            self.zoom_secret_key == settings.ZOOM_PROJECT_API_SECRET

    @property
    def teams_zoom_rooms(self):
        """
            Get ZoomRoom objects for this Project
        """
        zoom_rooms = ZoomRoom.objects.none()
        if self.project.teams.exists():
            zoom_rooms = ZoomRoom.objects.filter(
                object_id__in=self.project.teams.values_list('id', flat=True),
                content_type__id=ContentType.objects.get_for_model(
                    self.project.teams.first(),
                ).id,
            )

        return zoom_rooms
