from django.apps import AppConfig


class AgreementConfig(AppConfig):
    name = 'agreement'
    verbose_name = 'Agreement'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
