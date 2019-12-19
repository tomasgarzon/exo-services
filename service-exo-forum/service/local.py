import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'False'))
ADMIN_PANEL = eval(os.environ.get('ADMIN_PANEL', 'True'))

SOURCE_NAME = os.environ.get('SOURCE_NAME', 'local')
IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'service-exo-forum')

PORT = os.environ.get('PORT', '8000')
ROOT = '/:{}'.format(PORT)

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', '*')]

ADMINS = (
    ('ExOAdmin', os.environ.get('ADMIN_EMAIL', 'devops@openexo.com')),
)

MANAGERS = ADMINS

SERVER_EMAIL = 'noreply@openexo.com'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'service_exo_forum'),
        'USER': os.environ.get('DB_USER', 'exolever'),
        'PASSWORD': os.environ.get('DB_PASS', 'exolever'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
    }
}


# Sentry

SENTRY_DSN = os.environ.get('SENTRY_DSN')
SENTRY_ENV = 'prod' if IS_PRODUCTION else 'sandbox'
SENTRY_VER = SOURCE_NAME


# Redis Database Matrix - 16 DataBases

# 0: exolever (and session)
# 1: celery-exolever
# 2: celery-exo-service-payments
# 3: celery-exo-service-forum
# 4: celery-exolever-test
# 7: celery-exo-service-conversations

# 15: django-channels

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_AUTH_DB = 0
REDIS_CELERY_DB = 16

# Nginx

FORCE_SCRIPT_NAME = os.environ.get('FORCE_SCRIPT_NAME', '/forum/')

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')
SERVICE_EXO_MAIL_HOST = os.environ.get('SERVICE_EXO_MAIL_HOST', '/mails/')
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'http://localhost:8000')
POPULATOR_MODE = eval(os.environ.get('POPULATOR_MODE', 'False'))
INSTALLED_APPS = []
