import json
import redis

from django.conf import settings
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


def send_notifications(topic, action, filterset, data, obj_name=None):
    CHANNEL_NAME = '{}.{}'.format(
        settings.SERVICE_SHORT_NAME,
        topic)
    REDIS_PREFIX = 'broker'
    connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_AUTH_DB,)

    payload = {
        'action': action,
        'object': obj_name,
        'payload': json.loads(CamelCaseJSONRenderer().render(data)),
    }

    redis_data = {
        'subscription': CHANNEL_NAME,
        'data': payload,
    }
    redis_data.update(filterset)
    return connection.publish(
        '{}{}'.format(REDIS_PREFIX, CHANNEL_NAME),
        json.dumps(redis_data))
