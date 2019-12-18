from django.apps import AppConfig


class RelationConfig(AppConfig):
    name = 'relation'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
