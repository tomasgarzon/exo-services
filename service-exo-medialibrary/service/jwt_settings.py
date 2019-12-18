from .local import EXOLEVER_HOST  # noqa
import os

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '6vj06c)fc=!9ot%7t6^r2v^=$5x-j*6*#kk))cg0e!9zcyp(y+')
URL_VALIDATE_USER_UUID = '{}/{}'.format(EXOLEVER_HOST, 'api/accounts/me/{}/')
URL_VALIDATE_USER_COOKIE = '{}/{}'.format(EXOLEVER_HOST, 'api/accounts/me/')
