from django.apps import AppConfig


class SprintAutomatedConfig(AppConfig):
    name = 'sprint_automated'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
