from django.apps import AppConfig


class ResourceConfig(AppConfig):
    name = 'resource'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
