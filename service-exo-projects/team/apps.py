from django.apps import AppConfig


class TeamConfig(AppConfig):
    name = 'team'

    def ready(self):
        from .signals import setup_signals
        from actstream import registry
        setup_signals()
        registry.register(self.get_model('Team'))
        registry.register(self.get_model('TeamStep'))
