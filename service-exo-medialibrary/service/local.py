import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'False'))

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
        'NAME': os.environ.get('DB_NAME', 'exolever_medialibrary'),
        'USER': os.environ.get('DB_USER', 'exolever'),
        'PASSWORD': os.environ.get('DB_PASS', 'exolever'),
        'HOST': os.environ.get('DB_HOST', 'postgres'),
    }
}

VIMEO_TOKEN = os.environ.get('VIMEO_TOKEN', 'XXX')
VIMEO_CLIENT_ID = os.environ.get('VIMEO_CLIENT_ID', 'XXX')
VIMEO_CLIENT_SECRET = os.environ.get('VIMEO_CLIENT_SECRET', 'XXX')

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'XXX')

FILESTACK_KEY = os.environ.get('FILESTACK_KEY', 'XXX')

# Must be True ONLY in production
UPLOAD_REAL = eval(os.environ.get("UPLOAD_REAL", 'False'))
FORCE_SCRIPT_NAME = os.environ.get("FORCE_SCRIPT_NAME", '/medialibrary/')


# Sentry

SENTRY_DSN = os.environ.get('SENTRY_DSN')
SENTRY_ENV = 'prod' if IS_PRODUCTION else 'sandbox'
SENTRY_VER = SOURCE_NAME


#  Redis Database Matrix - 16 DataBases

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
REDIS_CHANNELS_DB = 15

EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')
POPULATOR_MODE = eval(os.environ.get("POPULATOR_MODE", 'False'))
