import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ...tasks.webhook_stripe import StripeWebhookTask

logger = logging.getLogger('service')


@api_view(['POST'])
def process_webhook(request):
    payment_intent_id = request.data.get('data').get('object').get('id')
    notification_type = request.data.get('type')

    log_data = 'Payment-{}-{}'.format(
        payment_intent_id,
        notification_type,
    )
    logger.info('StripeWebhooks RECEIVED - {}'.format(log_data))

    try:
        assert payment_intent_id
        assert notification_type

        StripeWebhookTask().s(
            payment_intent_id=payment_intent_id,
            notification_type=notification_type,
            payload=request.data,
        ).apply_async()
        logger.info('StripeWebhooks PROCESSED - {}'.format(log_data))

    except AssertionError:
        log_data = 'StripeWebhooks ERROR - {}'.format(log_data)
        logger.error(log_data)

    return Response('ok', status=status.HTTP_200_OK)
