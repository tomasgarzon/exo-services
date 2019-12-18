from django.apps import AppConfig


class CirclesConfig(AppConfig):
    name = 'circles'

    def ready(self):
        from actstream import registry
        from .signals import setup_signals
        setup_signals()
        registry.register(self.get_model('Circle'))
