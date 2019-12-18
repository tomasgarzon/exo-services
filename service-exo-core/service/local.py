# -*- coding: utf-8 -*
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

ROOT = os.environ.get('DOMAIN_NAME', 'localhost')

# Study to use self.live_server_url instead of defining the DJANGO_LIVE_TEST_SERVER_ADDRESS env var
ROOT_TEST = 'localhost:8002'

# This branch will serve the exo-frontend in DEBUG mode
SOURCE_NAME = os.environ.get('SOURCE_NAME', 'devel')
IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))

SERVICE_NAME = os.environ.get('SERVICE_NAME', 'service-exo-core')

MASTER_PASSWORD = [os.environ.get('MASTER_PASSWORD', ''), ]
ZIPPED_FILES_PASSWORD = os.environ.get('ZIPPED_FILES_PASSWORD', 'abc')

ADMINS = (
    ('ExOAdmin', os.environ.get('ADMIN_EMAIL', 'devops@openexo.com')),
)

MANAGERS = ADMINS

# Support overriding the credentials form command line
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'service_exo_core'),
        'USER': os.environ.get('DB_USER', 'exolever'),
        'PASSWORD': os.environ.get('DB_PASS', 'exolever'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

SEND_TO = [os.environ.get('ADMIN_EMAIL', 'devops@openexo.com')]
MAIL_REPLY_TO = 'noreply@openexo.com'
SERVER_EMAIL = 'noreply@openexo.com'
INSTRUMENTATION_EMAIL = os.environ.get('INSTRUMENTATION_EMAIL', 'platform-metrics@openexo.com')

# ExO Foundations
EXO_FOUNDATIONS_EN = os.environ.get('PROJECT_CERTIFICATION_LEVEL_1_EN', 13)
EXO_FOUNDATIONS_ES = os.environ.get('PROJECT_CERTIFICATION_LEVEL_1_ES', 14)
PROJECT_CERTIFICATION_LEVEL_1_ITEMS = '{},{}'.format(EXO_FOUNDATIONS_EN or '', EXO_FOUNDATIONS_ES or '')
PROJECT_CERTIFICATION_LEVEL_1 = list(map(int, filter(lambda x: x != '', PROJECT_CERTIFICATION_LEVEL_1_ITEMS.split(','))))  # noqa
PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE = {}
if EXO_FOUNDATIONS_EN:
    PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE['en'] = EXO_FOUNDATIONS_EN
if EXO_FOUNDATIONS_ES:
    PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE['es'] = EXO_FOUNDATIONS_ES

DEBUG = eval(os.environ.get('DEBUG', 'False'))
DEBUG_GRAPHQL = eval(os.environ.get('DEBUG_GRAPHQL', 'False'))

MIDDLEWARE = []

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# TypeForm integrations

TYPEFORM_APIKEY = os.environ.get('TYPEFORM_APIKEY', '')


# Segment Integration

SEGMENT_WRITE_KEY = os.environ.get('SEGMENT_WRITE_KEY', None)

# Sentry

SENTRY_DSN = os.environ.get('SENTRY_DSN')
SENTRY_ENV = 'prod' if IS_PRODUCTION else 'sandbox'
SENTRY_VER = SOURCE_NAME

#  Redis Database Matrix - 16 DataBases

# 0: service-exo-core (and session)
# 1: celery-exolever
# 2: celery-exo-service-payments
# 3: celery-exo-service-opportunities
# 4: celery-exolever-test

# 15: django-channels

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_AUTH_DB = 0
REDIS_CELERY_DB = 1
REDIS_CHANNELS_DB = 15

REDIS_TEST_DB = 4

CELERY_SERVICE_BROKER_URL = os.environ.get(
    'BROKER_URL',
    'redis://{}:{}/{}'.format(
        REDIS_HOST,
        REDIS_PORT,
        REDIS_CELERY_DB
    )
)

# Intercom

INTERCOM_SECRET_KEY = os.environ.get('INTERCOM_SECRET_KEY', None)

# Microservices

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'http://localhost')
MEDIA_LIBRARY_HOST = os.environ.get('MEDIA_LIBRARY_HOST', '/medialibrary/')
SERVICE_EXO_MAIL_HOST = os.environ.get('SERVICE_EXO_MAIL_HOST', '/mails/')
SERVICE_CONVERSATIONS_HOST = os.environ.get('SERVICE_CONVERSATIONS_HOST', '/conversations/')
EXO_WEBSITE_HOST = os.environ.get('EXO_WEBSITE_HOST', '/website/')
SERVICE_EXO_PAYMENT_HOST = os.environ.get('SERVICE_EXO_PAYMENT_HOST', '/payments/')
SERVICE_EXO_AUTH_HOST = os.environ.get('SERVICE_EXO_AUTH_HOST', '/exo-auth/')
SERVICE_EXO_OPPORTUNITIES_HOST = os.environ.get('SERVICE_EXO_OPPORTUNITIES_HOST', '/opportunities/')
SERVICE_EXO_EVENTS_HOST = os.environ.get('SERVICE_EXO_EVENTS_HOST', '/events/')
SERVICE_EXO_PROJECTS_HOST = os.environ.get('SERVICE_EXO_PROJECTS_HOST', '/projects/')
SERVICE_JOBS_HOST = os.environ.get('SERVICE_JOBS_HOST', '/jobs/')

PAYMENT_SECRET_KEY = os.environ.get('PAYMENT_SECRET_KEY', '')

# Filestack

FILESTACK_KEY = os.environ.get('FILESTACK_KEY', '')

# Accredible

ACCREDIBLE_ENABLED = eval(os.environ.get('ACCREDIBLE_ENABLED', 'False'))
ACCREDIBLE_SANDBOX = eval(os.environ.get('ACCREDIBLE_SANDBOX', 'True'))

# HUBSPOT
HAPIKEY = os.environ.get('HAPIKEY', '')

# POPULATOR
POPULATOR_MODE = eval(os.environ.get('POPULATOR_MODE', 'False'))

# Lambda functions

PLACE_KEY = os.environ.get('PLACE_KEY', '')
PLACE_TIMEZONE_URL = os.environ.get('PLACE_TIMEZONE_URL', '')  # noqa
ZOOM_URL = os.environ.get('ZOOM_URL', '')

# Metrics
GOOGLE_ANALYTIC_ID = os.environ.get('GOOGLE_ANALYTIC_ID', '')
RECAPTCHA_ENABLED = eval(os.environ.get('RECAPTCHA_ENABLED', 'False'))
