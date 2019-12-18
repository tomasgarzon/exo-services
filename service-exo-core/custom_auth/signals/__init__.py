from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed

from exo_accounts.signals.signals_user import update_user_title_handler
from exo_accounts.signals_define import (
    signal_exo_user_new_email_address_unverified,
    signal_exo_user_title,
)
from exo_accounts.signals_define import signal_exo_user_request_new_password

from .signal_user_emailaddress import (
    request_user_emailadress_handler,
    change_password_handler)
from .signal_user_notification import (
    signal_user_post_save_handler,
    signal_user_permissions_handler)
from .signal_segment_events import signal_segment_event_user_save_handler


def setup_signals():
    EmailAddress = apps.get_model(app_label='exo_accounts',
                                  model_name='EmailAddress')
    signal_exo_user_new_email_address_unverified.connect(
        request_user_emailadress_handler,
        sender=EmailAddress,
    )

    signal_exo_user_request_new_password.connect(
        change_password_handler,
        sender=get_user_model(),
    )

    signal_exo_user_title.connect(
        update_user_title_handler
    )

    post_save.connect(
        signal_user_post_save_handler,
        sender=get_user_model())

    post_save.connect(
        signal_segment_event_user_save_handler,
        sender=get_user_model(),
    )

    m2m_changed.connect(
        signal_user_permissions_handler,
        sender=get_user_model().user_permissions.through)
