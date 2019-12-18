from django.conf import settings

from ..models import ZoomSettings
from .define import signal_create_zoom_settings


def create_zoom_settings(sender, *args, **kwargs):
    project_settings = ZoomSettings(
        zoom_api_key=settings.ZOOM_PROJECT_API_KEY,
        zoom_secret_key=settings.ZOOM_PROJECT_API_SECRET,
        project=sender,
    )
    project_settings.save()


def new_project_created(sender, instance, created, *args, **kwargs):
    if created and not hasattr(instance, 'zoom_settings'):
        if hasattr(instance, 'project_ptr'):
            instance = instance.project_ptr
        signal_create_zoom_settings.send(sender=instance)
