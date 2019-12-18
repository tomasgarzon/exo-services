from django.apps import AppConfig


class JobConfig(AppConfig):
    name = 'job'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
