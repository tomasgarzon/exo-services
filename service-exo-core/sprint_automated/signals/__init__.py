from django.apps import apps
from django.db.models.signals import post_save

from .project import post_save_project


def setup_signals():
    Project = apps.get_model(
        app_label='project', model_name='Project',
    )

    post_save.connect(post_save_project, sender=Project)
