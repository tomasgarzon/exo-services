"""
Django settings for service-exo-core project.

Generated by 'django-admin startproject' using Django 1.9.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""
import os
import sys
import logging

from django.utils.translation import ugettext_lazy as _

from exo_accounts.authentication_backends import EXO_AUTHENTICATION_BACKENDS
from custom_messages.user_active_statements import REGULAR_USER, CONSULTANT_USER

from .local import *  # noqa
from .external import *  # noqa
from .apps import INSTALLED_APPS as APPS  # noqa
from .logging import LOGGING  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND_NAME = 'OpenExO'
SERVICE_SHORT_NAME = SERVICE_NAME.split('-')[-1]  # noqa

TEST_MODE = sys.argv[1:2] == ['test'] or 'py.test' in sys.argv[0]

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    logging.disable(logging.CRITICAL)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '(@ld*aiy5419but+akxofqmng1_p8c(57w1772hnoe58ydui^7')

INSTALLED_APPS = APPS

TEST_RUNNER = 'test_utils.TestRunner'

for arg in sys.argv:
    COVERAGE = True if arg == '--with-coverage' else False

if COVERAGE:
    TEST_RUNNER = 'test_utils.CoverageTestRunner'

MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'consultant.middleware.ConsultantActivationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'custom_auth.jwt_middleware.JWTAuthenticationMiddleware',
    'ecosystem.middleware.EcosystemActivityMiddleware',
]

ROOT_URLCONF = 'service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'custom_auth.context_processors.jwt',
                'frontend.context_processors.frontend',
            ],
        },
    },
]

WSGI_APPLICATION = 'service.wsgi.application'

# AUTH configuration

AUTH_USER_MODEL = 'exo_accounts.User'
AUTH_SECRET_KEY = os.environ.get('AUTH_SECRET_KEY', 'o134467ss##w@kusnw@)1d2uu%#blvj!+1ej6obgc@%q=wr)&4')

EXO_ACCOUNTS_EMAIL_VERIFIACTION_URL_VIEW_NAME = 'public:mails:email-verification-url'

ANONYMOUS_USER_ID = None
ANONYMOUS_USER_NAME = None
GUARDIAN_MONKEY_PATCH = False

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # default
    'guardian.backends.ObjectPermissionBackend',
) + EXO_AUTHENTICATION_BACKENDS

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]

# Language config

LANGUAGE_CODE = 'en-us'

LANGUAGE_EN = 'en'
LANGUAGE_ES = 'es'
LANGUAGE_PT = 'pt'
LANGUAGE_JA = 'ja'
LANGUAGE_ZH = 'zh-hans'

LANGUAGE_DEFAULT = LANGUAGE_EN

LANGUAGES = (
    (LANGUAGE_EN, _('English')),
    (LANGUAGE_ES, _('Spanish')),
    (LANGUAGE_PT, _('Portuguese')),
    (LANGUAGE_JA, _('Japanese')),
    (LANGUAGE_ZH, _('Simplified Chinese')),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

PROTECTED_ROOT = os.path.join(BASE_DIR, 'media/protected')
INTERNAL_REDIRECT = 'internal_redirect'
PROTECTED_URL = '%s/%s/' % (ROOT.replace('https://', ''), 'media/protected')

LOGOUT_URL = '/accounts/login/'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/redirect-profile/'

# FAKER SETTINGS
FAKER_SETTINGS_LOCALE = 'en_GB'

SITE_ID = 1

DATE_FORMAT = 'b j, Y'
DATETIME_FORMAT = 'b j, Y H:i'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CUSTOM_EXO_MESSAGE_USER_ACTIVE_STATEMENT = {REGULAR_USER, CONSULTANT_USER}
SERVER_VERSION_1 = 'https://omega.exolever.com'

# Redis
SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_AUTH_DB,
    'prefix': 'session',
    'socket_timeout': 1,
    'retry_on_timeout': False
}

# CELERY

# Seconds to wait for the worker to acknowledge the task before the message
# is redelivered to another worker
CELERY_SERVICE_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 999000}

# Metric url
METRIC_URL = os.environ.get('METRIC_URL', '')

# HUBSPOT ENVIRONMENT
HS_PIPELINE_PREFIX = os.environ.get('HS_PIPELINE_PREFIX', 'sb_')

if DEBUG:
    from .settings_debug import *  # noqa

if TEST_MODE:
    from .settings_test import *  # noqa