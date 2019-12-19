import json
import redis

from django.conf import settings
from djangorestframework_camel_case.render import CamelCaseJSONRenderer


def send_notifications(action, obj_name, user_uuid, data, renderer_class=CamelCaseJSONRenderer):
    CHANNEL_NAME = '{}.{}'.format(
        settings.SERVICE_SHORT_NAME,
        settings.SERVICE_SHORT_NAME)
    REDIS_PREFIX = 'broker'
    connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_AUTH_DB,)
    payload = {
        'action': action,
        'object': obj_name,
        'payload': json.loads(renderer_class().render(data)),
    }
    redis_data = {
        'subscription': CHANNEL_NAME,
        'data': payload,
        'uuid': str(user_uuid)
    }
    connection.publish(
        '{}{}'.format(REDIS_PREFIX, CHANNEL_NAME),
        json.dumps(redis_data))
