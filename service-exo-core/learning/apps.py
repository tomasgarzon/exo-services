from django.apps import AppConfig


class LearningConfig(AppConfig):
    name = 'learning'
    verbose_name = 'Learning'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
