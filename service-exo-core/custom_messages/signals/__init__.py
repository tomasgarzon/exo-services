from django.apps import apps
from django.db.models.signals import post_save, post_delete
from django.contrib.auth import get_user_model

from exo_accounts.signals_define import email_verified, signal_password_updated

from .signals_email_address_message import (
    email_address_handler,
    email_address_delete_handler,
    verified_handler,
)
from .signals_password_message import password_changed_handler


def setup_signals():

    EmailAddress = apps.get_model(
        app_label='exo_accounts',
        model_name='EmailAddress')

    post_save.connect(email_address_handler, sender=EmailAddress)
    post_delete.connect(email_address_delete_handler, sender=EmailAddress)
    email_verified.connect(verified_handler)

    signal_password_updated.connect(
        password_changed_handler,
        sender=get_user_model())
