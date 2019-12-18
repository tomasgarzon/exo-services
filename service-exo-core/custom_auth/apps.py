from django.apps import AppConfig
from django.contrib.auth import get_user_model


class AuthConfig(AppConfig):
    name = 'custom_auth'
    verbose_name = 'custom_auth'

    def ready(self):
        from .signals import setup_signals
        from actstream import registry
        setup_signals()
        registry.register(get_user_model())
