from django.conf import settings

from .tasks import SendMailTask


def send_email(message, to_addresses=[]):
    manual_send = True

    if not to_addresses:
        to_addresses = message.to_addresses
        if settings.IS_PRODUCTION:
            manual_send = False

    return SendMailTask().s(
        pk=message.pk,
        to_addresses=to_addresses,
        is_manually_sent=manual_send).apply_async()
