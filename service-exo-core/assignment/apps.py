from django.apps import AppConfig


class AssignmentConfig(AppConfig):
    name = 'assignment'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
