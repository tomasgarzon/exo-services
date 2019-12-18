import logging
import requests
from celery import shared_task

from django.conf import settings


SHARED_KEY = 'A5GGLDymZ7vCfjjy'
logger = logging.getLogger('metric')


@shared_task
def create_metric(user, category, action, label=None, value=None):
    if not label:
        label = settings.OPPORTUNITIES_METRIC_LABEL_OPP
    if not settings.METRIC_URL:
        return
    url = settings.METRIC_URL + '/metric/'
    metric_data = {
        'user': user,
        'category': category,
        'action': action,
        'label': label,
    }
    data = {
        'key': SHARED_KEY,
    }
    if value:
        metric_data['value'] = value

    new_data = metric_data.copy()
    new_data.update(data)
    logging.info('Calling to metric service {}'.format(metric_data))
    try:
        response = requests.post(url, json=new_data)
        logging.info('Metric stored {}'.format(response.json()))
    except requests.exceptions.RequestException as e:
        logging.error('Metric store error {}'.format(e))
    if not response.ok:
        logging.error('Metric store error {}'.format(response.content))
