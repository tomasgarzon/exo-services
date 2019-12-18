from django.apps import AppConfig


class UtilsConfig(AppConfig):
    name = 'utils'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
