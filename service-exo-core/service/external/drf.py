REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'utils.drf.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'utils.drf.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'utils.drf.authentication.UsernameAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_PARSER_CLASSES': [
        'utils.drf.parsers.LimitedFormParser',
        'rest_framework.parsers.MultiPartParser',
        'utils.drf.parsers.LimitedJSONParser',
    ],
}


# JWT Configuration
JWT_AUTH = {
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'custom_auth.jwt_response_payload_handler.jwt_response_payload_handler',
    'JWT_PAYLOAD_HANDLER': 'custom_auth.jwt_payload_handler.jwt_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'custom_auth.jwt_response_payload_handler.jwt_get_username_from_payload_handler'
}
