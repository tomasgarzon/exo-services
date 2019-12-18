import requests
import logging

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt


logger = logging.getLogger('service')


def get_unread_messages(opp_uuids, user_from):
    token = _build_jwt(user_from)
    host = settings.EXOLEVER_HOST + settings.SERVICE_CONVERSATIONS_HOST
    url = host + 'api/total/'
    headers = {'Authorization': 'Bearer ' + token}
    data = {
        'uuids': opp_uuids,
    }

    if not settings.POPULATOR_MODE:
        try:
            response = requests.post(url, data=data, headers=headers)
            return response.json()
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
    return []
