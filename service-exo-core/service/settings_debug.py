EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'utils.drf.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'utils.drf.authentication.UsernameAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'  # only for debug
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer'
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_PARSER_CLASSES': [
        'utils.drf.parsers.LimitedFormParser',
        'rest_framework.parsers.MultiPartParser',
        'utils.drf.parsers.LimitedJSONParser',
    ],
}


# Define these vara to use docker proxy
MICROSERVICES_DOCKER = True
LOCAL_DOCKER_PROXY = {
    'exo_jobs': {
        'base_url': 'http://0.0.0.0:8020',
        'prefix': 'jobs/',
    },
    'exo_exq': {
        'base_url': 'http://0.0.0.0:8019',
        'prefix': 'exq/',
    },
    'exo_events': {
        'base_url': 'http://0.0.0.0:8018',
        'prefix': 'events/',
    },
    'exo_projects': {
        'base_url': 'http://0.0.0.0:8017',
        'prefix': 'projects/',
    },
    'exo_auth': {
        'base_url': 'http://0.0.0.0:8014',
        'prefix': 'exo-auth/',
    },
    'exo_conversations': {
        'base_url': 'http://0.0.0.0:8013',
        'prefix': 'conversations/',
    },
    'exo_payments': {
        'base_url': 'http://0.0.0.0:8012',
        'prefix': 'payments/',
    },
    'exo_opportunities': {
        'base_url': 'http://0.0.0.0:8011',
        'prefix': 'opportunities/',
    },
    'exo_mail': {
        'base_url': 'http://0.0.0.0:8010',
        'prefix': 'mails/',
    },
    'exo_website': {
        'base_url': 'http://0.0.0.0:8005',
        'prefix': 'website/',
    },
    'exo_medialibrary': {
        'base_url': 'http://0.0.0.0:8001',
        'prefix': 'medialibrary/',
    },
}
