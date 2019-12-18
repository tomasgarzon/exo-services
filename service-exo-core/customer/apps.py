from django.apps import AppConfig


class CustomerConfig(AppConfig):
    name = 'customer'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
