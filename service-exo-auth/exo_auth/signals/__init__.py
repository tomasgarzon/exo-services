from django.db.models.signals import post_save, post_delete
from django.apps import apps
from django.contrib.auth import get_user_model

from ..settings import MM
from .signals_email_handler import email_address_handler
from .signals_user import (
    clear_unverified_email_addresses,
    post_save_user_perms)
from ..signals_define import signal_exo_user_request_new_password
from .signal_user_emailaddress import change_password_handler
from .signals_user_subscription import (
    create_user_subscription_handler,
    delete_user_subscription_handler)


def setup_signals():
    UserSubscription = apps.get_model('exo_auth', 'UserSubscription')
    post_save.connect(email_address_handler,
                      sender=get_user_model())
    post_save.connect(post_save_user_perms, sender=get_user_model())

    if MM.USER_DEACTIVATION_HANDLER_ON:
        post_save.connect(clear_unverified_email_addresses,
                          sender=get_user_model())

    signal_exo_user_request_new_password.connect(
        change_password_handler,
        sender=get_user_model(),
    )

    post_save.connect(
        create_user_subscription_handler,
        sender=UserSubscription)
    post_delete.connect(
        delete_user_subscription_handler,
        sender=UserSubscription)
