from django.conf import settings

import redis


class RedisConnection(object):
    def __init__(self, **kwargs):
        self.connection = self.create_connection()

    def create_connection(self):
        return redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_AUTH_DB,
        )
