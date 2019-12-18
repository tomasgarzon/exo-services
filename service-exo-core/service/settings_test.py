import os

from celery import current_app

from .local import ROOT_TEST, REDIS_TEST_DB

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_REDIS = None
METRIC_URL = ''
POPULATOR_MODE = True
ACCREDIBLE_ENABLED = False
RECAPTCHA_ENABLED = False
current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True

os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = ROOT_TEST
ROOT = 'http://' + ROOT_TEST
REDIS_AUTH_DB = REDIS_TEST_DB
