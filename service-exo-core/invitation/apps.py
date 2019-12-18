from django.apps import AppConfig


class InvitationConfig(AppConfig):
    name = 'invitation'
    verbose_name = 'Invitation'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
