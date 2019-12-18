from django.conf import settings
import requests
import logging


URL_GROUPS = '{}/api/accounts/groups/{}/'
logger = logging.getLogger('service')


def get_users_in_group(group_name):
    url = URL_GROUPS.format(
        settings.EXOLEVER_HOST,
        group_name)
    response = None

    try:
        response = requests.get(
            url,
            headers={'USERNAME': settings.AUTH_SECRET_KEY})
    except Exception as err:
        message = 'requests.Exception: {}'.format(err)
        logger.error(message)
        response = None

    if response and response.status_code == requests.codes.ok:
        return response.json().get('user_set')
    return None
