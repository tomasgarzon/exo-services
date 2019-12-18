from django.apps import AppConfig


class RegistrationConfig(AppConfig):
    name = 'registration'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
