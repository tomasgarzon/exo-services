# Example SocketShark configuration file
# For more settings, see socketshark/config_defaults.py

# Host and port to bind WebSockets.
import os

WS_HOST = '0.0.0.0'
WS_PORT = '8000'

SOURCE_NAME = os.environ.get('SOURCE_NAME', 'local')
IS_PRODUCTION = eval(os.environ.get('IS_PRODUCTION', 'False'))
SERVICE_NAME = os.environ.get('SERVICE_NAME')

# Redis options
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_AUTH_DB = 0
EXOLEVER_HOST = os.environ.get('EXOLEVER_HOST', 'http://service-exo-broker')

REDIS = {
    'host': REDIS_HOST,
    'port': REDIS_PORT,
    'db': REDIS_AUTH_DB,
    'channel_prefix': 'broker',
}

# Authentication (currently only "ticket" authentication is supported)
AUTHENTICATION = {
    'ticket': {
        # API endpoint to validate the ticket and exchange it for auth info.
        'validation_url': EXOLEVER_HOST + '/exo-auth/api/ticket/',

        # Fields that the validation endpoint returns.
        'auth_fields': ['uuid', 'email'],
    }
}

# List of services
SERVICES = {
    'conversations': {
        # Whether to always require authentication. When False, anonymous
        # sessions are supported even if an authorizer is configured.
        'require_authentication': True,
        'on_subscribe': '{}/exo-auth/api/on_subscribe/'.format(EXOLEVER_HOST),
        'on_unsubscribe': '{}/exo-auth/api/on_unsubscribe/'.format(EXOLEVER_HOST),
        'filter_fields': ['uuid'],
    },
    'opportunities': {
        # Whether to always require authentication. When False, anonymous
        # sessions are supported even if an authorizer is configured.
        'require_authentication': True,
        'on_subscribe': '{}/exo-auth/api/on_subscribe/'.format(EXOLEVER_HOST),
        'on_unsubscribe': '{}/exo-auth/api/on_unsubscribe/'.format(EXOLEVER_HOST),
        'filter_fields': ['uuid'],
    },
    'core': {
        # Whether to always require authentication. When False, anonymous
        # sessions are supported even if an authorizer is configured.
        'require_authentication': True,
        'on_subscribe': '{}/exo-auth/api/on_subscribe/'.format(EXOLEVER_HOST),
        'on_unsubscribe': '{}/exo-auth/api/on_unsubscribe/'.format(EXOLEVER_HOST),
        'filter_fields': ['uuid'],
    },
    'auth': {
        'require_authentication': True,
        'filter_fields': ['uuid']
    },
    'projects': {
        # Whether to always require authentication. When False, anonymous
        # sessions are supported even if an authorizer is configured.
        'require_authentication': True,
        'on_subscribe': '{}/exo-auth/api/on_subscribe/'.format(EXOLEVER_HOST),
        'on_unsubscribe': '{}/exo-auth/api/on_unsubscribe/'.format(EXOLEVER_HOST),
        'filter_fields': ['uuid'],
    },
}
