import os
from .local import *  # noqa

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '6vj06c)fc=!9ot%7t6^r2v^=$5x-j*6*#kk))cg0e!9zcyp(y+')
JWT_VERIFY_EXPIRATION = False
JWT_VERIFY = True
JWT_LEEWAY = 0
JWT_AUDIENCE = None
JWT_ISSUER = None
JWT_ALGORITHM = 'HS256'

JWT_AUTH = {
    'JWT_DECODE_HANDLER': 'utils.auth_helpers.jwt_decode_handler',
    'JWT_PAYLOAD_GET_USERNAME_HANDLER': 'utils.auth_helpers.jwt_get_username_from_payload_handler',
    'JWT_PAYLOAD_HANDLER': 'utils.auth_helpers.jwt_payload_handler',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_SECRET_KEY': JWT_SECRET_KEY,
}

URL_VALIDATE_USER_UUID = '{}/{}'.format(EXOLEVER_HOST, 'api/accounts/me/{}/')
