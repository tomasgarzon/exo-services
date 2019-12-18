from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = 'project'

    def ready(self):

        from .signals import setup_signals
        setup_signals()
