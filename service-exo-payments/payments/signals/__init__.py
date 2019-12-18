from django.apps import apps
from django.db.models.signals import post_save, pre_save

from ..signals_define import signal_payment_received, payment_status_changed

from .payment import (
    new_payment_created,
    send_email_notification,
    pre_new_payment_created,
    pre_save_payment_vat,
    payment_status_changed_handler,
)
from .payment_received import payment_received_handler


def setup_signals():

    Payment = apps.get_model(
        app_label='payments',
        model_name='Payment')

    post_save.connect(new_payment_created, sender=Payment)
    post_save.connect(send_email_notification, sender=Payment)

    pre_save.connect(pre_new_payment_created, sender=Payment)
    pre_save.connect(pre_save_payment_vat, sender=Payment)

    signal_payment_received.connect(payment_received_handler)

    payment_status_changed.connect(payment_status_changed_handler)
