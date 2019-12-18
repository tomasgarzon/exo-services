from django.apps import AppConfig


class GenericProjectConfig(AppConfig):
    name = 'generic_project'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
