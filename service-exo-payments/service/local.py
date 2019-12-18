import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'False'))
ADMIN_PANEL = eval(os.environ.get('ADMIN_PANEL', 'True'))

SOURCE_NAME = os.environ.get('SOURCE_NAME', 'local')
IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))
SERVICE_NAME = os.environ.get('SERVICE_NAME')

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
        'NAME': os.environ.get('DB_NAME', 'service_exo_payments'),
        'USER': os.environ.get('DB_USER', 'exolever'),
        'PASSWORD': os.environ.get('DB_PASS', 'exolever'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
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
# 3: celery-exo-service-opportunities
# 4: celery-exolever-test
# 7: celery-exo-service-conversations

# 15: django-channels

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_AUTH_DB = 0
REDIS_CELERY_DB = 2

# Nginx

FORCE_SCRIPT_NAME = os.environ.get('FORCE_SCRIPT_NAME', '/payments/')

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')
SERVICE_EXO_MAIL_HOST = os.environ.get('SERVICE_EXO_MAIL_HOST', '/mails/')
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'localhost')
POPULATOR_MODE = eval(os.environ.get('POPULATOR_MODE', 'False'))
METRIC_URL = os.environ.get('METRIC_URL', '')
INSTALLED_APPS = []


# ##
# Stripe
# ##

STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'at(t8u!3qiq8s*6eufc@i@(g^hknvzs$@3#1ka)9rxt8e4r9f2')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '&&g&ctwe4@4eq#v)1q*99(&06*3kc1+%f(s@*42l(ozukzfaef')

try:
    assert STRIPE_SECRET_KEY
    assert STRIPE_PUBLIC_KEY
except AssertionError:
    raise Exception('Please provide Stripe API keys')

EMAIL_NOTIFICATIONS_FROM = 'finance@openexo.com'

# 0: exolever
# 1: celery-exolever
# 2: celery-exo-service-payments
# 3: celery-exo-service-opportunities
# 4: celery-exolever-test
