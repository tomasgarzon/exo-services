# -*- coding: utf-8 -*-

# Third Party Library
from celery import current_app
import redis

from django.conf import settings

DATA_MIGRATIONS = []


def redis_clear(prefix='test__'):
    settings.REDIS_AUTH_DB = settings.REDIS_TEST_DB

    connection = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_AUTH_DB,
    )
    connection.flushall()


def celery_fix():
    settings.CELERY_ALWAYS_EAGER = True
    current_app.conf.CELERY_ALWAYS_EAGER = True
    settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
    current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    settings.DEBUG = True
    settings.TEST_MODE = True
