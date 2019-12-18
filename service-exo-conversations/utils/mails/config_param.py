import requests
import logging

from rest_framework_jwt.settings import api_settings
from auth_uuid.jwt_helpers import _build_jwt

from django.conf import settings


logger = logging.getLogger('service')
URL_CONFIG_PARAMS = '/api/account-config/config_param/{}/'


def get_config_param_remote(user_from):
    headers = {
        'Authorization': '{} {} '.format(
            api_settings.JWT_AUTH_HEADER_PREFIX,
            _build_jwt(user_from))}
    url = URL_CONFIG_PARAMS.format(user_from.uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def enabled_config_param(user_from, param_name):
    values = get_config_param_remote(user_from)
    if values is not None:
        config_param = list(filter(lambda x: x['name'] == param_name, values))
        try:
            return config_param[0]['value']
        except IndexError:
            return False
    return False
