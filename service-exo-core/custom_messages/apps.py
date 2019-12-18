from django.apps import AppConfig


class CustomMessagesConfig(AppConfig):
    name = 'custom_messages'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
