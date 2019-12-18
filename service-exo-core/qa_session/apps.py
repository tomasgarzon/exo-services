from django.apps import AppConfig


class QaSessionConfig(AppConfig):
    name = 'qa_session'

    def ready(self):

        from .signals import setup_signals
        setup_signals()
