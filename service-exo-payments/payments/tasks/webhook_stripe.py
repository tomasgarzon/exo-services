import logging

from django.conf import settings

from service.celery import app

from celery import Task

from ..models import Payment


logger = logging.getLogger('celery')


class StripeWebhookTask(Task):
    name = 'Stripe Webhook Notification'
    ignore_result = False

    def run(self, *args, **kwargs):
        payment_intent_id = kwargs.get('payment_intent_id')
        notification_type = kwargs.get('notification_type')
        webhook_payload = kwargs.get('payload')

        log_data = 'Payment-{}-{}'.format(
            payment_intent_id,
            notification_type,
        )
        logger.info('StripeWebhookTask RUN - {}'.format(payment_intent_id))

        try:
            payment = Payment.objects.get(
                intent_id=payment_intent_id,
                status__in=[
                    settings.PAYMENTS_CH_RECEIVED,
                    settings.PAYMENTS_CH_PENDING,
                    settings.PAYMENTS_CH_ERROR,
                ]
            )
            payment_object = webhook_payload.get('data').get('object')
            if notification_type == settings.PAYMENTS_STRIPE_PAYMENT_INTENT_WEBHOOK_TYPE_SUCCESS:
                payment_id = payment_object.get('charges').get('data')[0].get('id')
                payment.payment_intent_success(payment_id)

                logger.info('StripeWebhookTask DONE - {}'.format(log_data))

            elif notification_type == settings.PAYMENTS_STRIPE_PAYMENT_INTENT_WEBHOOK_TYPE_ERROR:
                error_data = payment_object.get('last_payment_error')
                payment.payment_intent_fail()

                logger.info('StripeWebhookTask ERROR - {} {} {}'.format(
                    error_data.get('code'),
                    error_data.get('message'),
                    log_data,
                ))

        except Payment.DoesNotExist:
            if settings.IS_PRODUCTION:
                logger.error('StripeWebhookTask NOT FOUND - {}'.format(log_data))


app.tasks.register(StripeWebhookTask())
