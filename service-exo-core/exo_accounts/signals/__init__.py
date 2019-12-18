from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.apps import apps

from ..settings import MM
from .signals_email_handler import email_address_handler
from .signals_user import (
    clear_unverified_email_addresses,
    post_save_user_perms,
    post_save_user_username)
from .signals_user_redis import (
    check_redis_user_cache,
    check_new_active_email_address)


def setup_signals():

    EmailAddress = apps.get_model('exo_accounts', 'EmailAddress')

    post_save.connect(email_address_handler, sender=get_user_model())
    post_save.connect(post_save_user_perms, sender=get_user_model())
    post_save.connect(post_save_user_username, sender=get_user_model())

    if MM.USER_DEACTIVATION_HANDLER_ON:
        post_save.connect(clear_unverified_email_addresses, sender=get_user_model())

    post_save.connect(check_new_active_email_address, sender=EmailAddress)
    post_save.connect(check_redis_user_cache, sender=get_user_model())
