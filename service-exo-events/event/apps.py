from django.apps import AppConfig


class EventConfig(AppConfig):
    name = 'event'
    verbose_name = 'Event'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
