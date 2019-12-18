from django.apps import AppConfig


class ExoHubConfig(AppConfig):
    name = 'exo_hub'

    def ready(self):
        from actstream import registry
        from .signals import setup_signals
        registry.register(self.get_model('ExOHub'))
        setup_signals()
