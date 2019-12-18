from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    name = 'marketplace'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
