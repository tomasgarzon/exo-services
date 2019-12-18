from django.apps import AppConfig


class ExOCertificationConfig(AppConfig):
    name = 'exo_certification'
    verbose_name = 'ExO Certification'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
