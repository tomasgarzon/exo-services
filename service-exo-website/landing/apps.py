from django.apps import AppConfig


class LandingConfig(AppConfig):
    name = 'landing'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
