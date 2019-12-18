from datetime import datetime
import uuid

from django.conf import settings

from payments.signals_define import signal_payment_received
from utils.dates import increase_date
from utils.random import build_hash

from ..tasks import SendPaymentEmailTask


def new_payment_created(instance, *args, **kwargs):
    created = kwargs.get('created', False)

    if created:
        instance._hash_code = build_hash()
        instance.save(update_fields=['_hash_code'])


def send_email_notification(instance, *args, **kwargs):
    created = kwargs.get('created', False)
    if created and instance.is_pending and instance.send_by_email:
        scheduled_time = increase_date(
            seconds=settings.PAYMENTS_PAYMENT_TASK_DELAY_SECONDS,
            date=datetime.now(),
        )
        SendPaymentEmailTask().s(
            payment_pk=instance.pk,
        ).apply_async(eta=scheduled_time)


def pre_new_payment_created(sender, instance, *args, **kwargs):
    if instance.uuid is None:
        instance.uuid = uuid.uuid4()


def pre_save_payment_vat(sender, instance, *args, **kwargs):
    is_spain = instance.country_code == settings.PAYMENTS_COUNTRY_SPAIN
    can_update = instance.status in settings.PAYMENTS_VALID_STATUS_UPDATE
    vat_is_zero = instance.vat == 0

    if is_spain and vat_is_zero and can_update:
        instance.vat = settings.PAYMENTS_VAT_DEFAULT


def payment_status_changed_handler(sender, payment, *args, **kwargs):
    if payment.status == settings.PAYMENTS_CH_PAID:
        signal_payment_received.send(
            sender=payment.__class__,
            payment=payment,
        )
