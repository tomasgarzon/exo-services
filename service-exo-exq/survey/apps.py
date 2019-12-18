from django.apps import AppConfig


class SurveyConfig(AppConfig):
    name = 'survey'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
