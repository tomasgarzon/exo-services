import requests
import logging

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt


URL_CREATE_USER = '{}/api/accounts/signup-auth/'
URL_CHECK_EMAIL = '{}/api/accounts/user/'

logger = logging.getLogger('service')


def create_remote_user(user_from, project, participant):
    headers = {'Authorization': 'Bearer ' + _build_jwt(user_from)}
    url = URL_CREATE_USER.format(settings.EXOLEVER_HOST)
    if settings.POPULATOR_MODE and not settings.TEST_MODE:
        return None

    logger.info('SyncParticipant: {}-{}'.format(participant.name, participant.email))

    data = {
        'short_name': participant.name,
        'full_name': participant.name,
        'email': participant.email,
        'uuid': participant.user.uuid.__str__(),
        'is_superuser': False,
        'is_staff': False,
        'is_active': True,
        'password': project.settings.launch['default_password']
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        assert response.status_code == requests.codes.created
        return response.json()
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)


def check_if_exists_email(email):
    headers = {'USERNAME': settings.AUTH_SECRET_KEY}
    url = URL_CHECK_EMAIL.format(settings.EXOLEVER_HOST)
    if settings.POPULATOR_MODE:
        return None, False

    logger.info('Search by email: {}'.format(email))

    try:
        response = requests.get(url + '?search={}'.format(email), headers=headers)
        assert response.status_code == requests.codes.ok
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)

    data = response.json()
    try:
        return data[0], True
    except IndexError:
        return None, False
