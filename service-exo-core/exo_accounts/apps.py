from django.apps import AppConfig


class ExOAccountsConfig(AppConfig):
    name = 'exo_accounts'
    verbose_name = 'ExOAccounts'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
