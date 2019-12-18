from django.apps import AppConfig


class TypeformConfig(AppConfig):
    name = 'typeform'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
