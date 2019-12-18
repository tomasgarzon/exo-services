from django.apps import AppConfig


class EcosystemConfig(AppConfig):
    name = 'ecosystem'
    verbose_name = 'Ecosystem'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
