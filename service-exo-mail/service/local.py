import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'False'))
ADMIN_PANEL = eval(os.environ.get('ADMIN_PANEL', 'False'))

SOURCE_NAME = os.environ.get('SOURCE_NAME', 'local')
IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'service-exo-mail')

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', '*')]

ADMINS = (
    ('ExOAdmin', os.environ.get('ADMIN_EMAIL', 'devops@openexo.com')),
)

MANAGERS = ADMINS

MAIL_REPLY_TO = 'noreply@openexo.com'
SERVER_EMAIL = 'noreply@openexo.com'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.environ.get('DB_NAME', 'service_exo_mail'),
        'USER': os.environ.get('DB_USER', 'exolever'),
        'PASSWORD': os.environ.get('DB_PASS', 'exolever'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
    }
}

# Mjml

MJML_BACKEND_MODE = 'cmd'
MJML_EXEC_CMD = './mjml/mjml'


# Mail
MAILER_AWS_BUCKET = os.environ.get('MAILER_AWS_BUCKET', '')
MAILER_AUTOSEND = eval(os.environ.get('MAILER_AUTOSEND', 'False'))
MAILER_EMAIL_BACKEND = os.environ.get(
    'MAILER_EMAIL_BACKEND', 'sendgrid_backend.SendgridBackend')
SENDGRID_SANDBOX_MODE_IN_DEBUG = False
SENDGRID_TRACK_EMAIL_OPENS = True
SENDGRID_TRACK_EMAIL_CLICKS = True
SENDGRID_SUBSCRIPTION_ENABLE = True
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')

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

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_AUTH_DB = 0
REDIS_CELERY_DB = 11

# Nginx

FORCE_SCRIPT_NAME = os.environ.get('FORCE_SCRIPT_NAME', '/mails/')

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')
DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'localhost')
INSTALLED_APPS = []
