from django.apps import AppConfig


class ZoomProjectConfig(AppConfig):
    name = 'zoom_project'
    verbose_name = 'Zoom'

    def ready(self):

        from .signals import setup_signals
        setup_signals()
