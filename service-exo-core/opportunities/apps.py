from django.apps import AppConfig


class OpportunitiesConfig(AppConfig):
    name = 'opportunities'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
