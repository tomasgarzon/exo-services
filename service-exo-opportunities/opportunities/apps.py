from django.apps import AppConfig


class OpportunitiesConfig(AppConfig):
    name = 'opportunities'

    def ready(self):
        from actstream import registry
        from .signals import setup_signals
        setup_signals()
        registry.register(self.get_model('Opportunity'))
