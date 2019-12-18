import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'False'))

SOURCE_NAME = os.environ.get('SOURCE_NAME', 'local')
IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))
SERVICE_NAME = os.environ.get('SERVICE_NAME', 'service-exo-website')

ALLOWED_HOSTS = [os.environ.get('ALLOWED_HOSTS', '*')]

ADMINS = (
    ('ExOAdmin', os.environ.get('ADMIN_EMAIL', 'devops@openexo.com')),
)

MANAGERS = ADMINS

SERVER_EMAIL = 'noreply@openexo.com'

SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'exolever_exo_website'),
        'USER': os.environ.get('DB_USER', 'exolever'),
        'PASSWORD': os.environ.get('DB_PASS', 'exolever'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
    }
}

EXO_WEBSITE_DOMAIN = os.environ.get('EXO_WEBSITE_DOMAIN', 'https://workshops.openexo.com')

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')
SERVICE_EVENTS_HOST = os.environ.get('SERVICE_EVENTS_HOST', '/events/')
INSTALLED_APPS = []


# Sentry

SENTRY_DSN = os.environ.get('SENTRY_DSN')
SENTRY_ENV = 'prod' if IS_PRODUCTION else 'sandbox'
SENTRY_VER = SOURCE_NAME
