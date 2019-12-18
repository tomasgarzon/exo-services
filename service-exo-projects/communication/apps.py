from django.apps import AppConfig


class CommunicationConfig(AppConfig):
    name = 'communication'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
