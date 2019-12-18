from django.conf import settings

from ..tasks import SendPaymentReceivedEmailTask


def can_generate_invoice(payment):
    has_invoicing_data = True
    is_tokens = payment.alternative_payment_mode == settings.PAYMENTS_CH_ALTERNATIVE_PAYMENT_TOKENS
    invoicing_fields = ['_type', 'country_code', 'country', 'full_name', 'address', 'tax_id']

    for field in invoicing_fields:
        if not getattr(payment, field):
            has_invoicing_data = False
            break

    return has_invoicing_data and not is_tokens


def payment_received_handler(sender, payment, *args, **kwargs):
    payment.notify_webhook()

    if can_generate_invoice(payment):
        payment.generate_invoice()
        if payment.send_invoice:
            SendPaymentReceivedEmailTask().s(
                payment_pk=payment.pk).apply_async()
