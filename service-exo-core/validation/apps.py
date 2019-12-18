from django.apps import AppConfig


class ValidationConfig(AppConfig):
    name = 'validation'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
