from django.apps import AppConfig


class ConsultantConfig(AppConfig):
    name = 'consultant'
    verbose_name = 'Consultant'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
