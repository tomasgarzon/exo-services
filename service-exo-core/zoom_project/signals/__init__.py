from django.apps import apps
from django.db.models.signals import post_save

from .define import signal_create_zoom_settings
from .zoom_room import post_save_room
from .zoom_settings import (
    create_zoom_settings,
    new_project_created
)


def setup_signals():

    ZoomRoom = apps.get_model(
        app_label='zoom_project', model_name='ZoomRoom',
    )
    Project = apps.get_model(
        app_label='project', model_name='Project',
    )

    post_save.connect(post_save_room, sender=ZoomRoom)

    # connect all subclasses of base content item too
    for subclass in Project.__subclasses__():
        post_save.connect(new_project_created, sender=subclass)
    post_save.connect(new_project_created, sender=Project)
    signal_create_zoom_settings.connect(create_zoom_settings)
