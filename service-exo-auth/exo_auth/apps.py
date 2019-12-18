from django.apps import AppConfig


class ExoAuthConfig(AppConfig):
    name = 'exo_auth'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
