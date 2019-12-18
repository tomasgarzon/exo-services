from django.conf import settings

import redis
import json


def send_notifications(action, user_uuid, data):
    CHANNEL_NAME = '{}.{}'.format(
        settings.SERVICE_SHORT_NAME,
        settings.SERVICE_SHORT_NAME)
    REDIS_PREFIX = 'broker'
    connection = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_AUTH_DB,)
    data.update({'action': action})
    redis_data = {
        'subscription': CHANNEL_NAME,
        'data': data,
        'uuid': str(user_uuid)}
    connection.publish(
        '{}{}'.format(REDIS_PREFIX, CHANNEL_NAME),
        json.dumps(redis_data))
