import requests
import logging

from django.conf import settings

from custom_auth.jwt_helpers import _build_jwt


URL_VIEW_PROJECT = 'api/view-project/'
logger = logging.getLogger('service')


def get_projects(user):
    headers = {'Authorization': 'Bearer ' + _build_jwt(user)}
    url = '{}{}{}'.format(
        settings.EXOLEVER_HOST,
        settings.SERVICE_EXO_PROJECTS_HOST,
        URL_VIEW_PROJECT)
    if settings.POPULATOR_MODE:
        return []
    try:
        response = requests.get(url, headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()['results']
    except Exception as e:
        logger.error('Can not access to exo-projects service')
        logger.error('{}'.format(e))
        return []
