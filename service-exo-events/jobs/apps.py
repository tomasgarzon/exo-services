from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = 'jobs'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
