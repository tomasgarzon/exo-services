import requests
import logging

from django.conf import settings

logger = logging.getLogger('celery-task')
URL_RECIPIENTS = '/api/accounts/user/can-receive-opportunities/'


def _get_recipients():
    recipients = []
    url = '{}{}'.format(settings.EXOLEVER_HOST, URL_RECIPIENTS)

    try:
        response = requests.get(
            url,
            headers={'USERNAME': settings.AUTH_SECRET_KEY})
    except Exception as err:
        message = 'NewOpportunityTask - requests.Exception: {}'.format(err)
        logger.error(message)
        response = None

    if response and response.status_code == requests.codes.ok:
        recipients = response.json()

    return recipients
