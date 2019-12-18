from django.apps import AppConfig


class WorkshopConfig(AppConfig):
    name = 'workshop'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
