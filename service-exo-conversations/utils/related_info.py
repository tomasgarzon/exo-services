import logging

from django.conf import settings
from rest_framework_jwt.settings import api_settings

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.utils.user_wrapper import UserWrapper
import requests


logger = logging.getLogger('service')


def _get_headers(user_from):
    return {
        'Authorization': '{} {}'.format(
            api_settings.JWT_AUTH_HEADER_PREFIX,
            _build_jwt(user_from))}


def get_info_opportunities(user_from, opportunity_uuid):
    URL = '{}api/admin-opportunity/{}/'
    headers = _get_headers(user_from)
    url = URL.format(
        settings.SERVICE_OPPORTUNITIES_HOST, opportunity_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def get_info_core_project(user_from, project_uuid):
    URL = '/api/project/admin-project/{}/'.format(project_uuid)
    headers = _get_headers(user_from)
    url = URL.format(project_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def get_info_exo_project(user_from, project_uuid):
    URL = '{}api/admin-project/{}/'
    headers = _get_headers(user_from)
    url = URL.format(
        settings.SERVICE_PROJECTS_HOST, project_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def get_info_related(conversation, user_from):

    if conversation._type == settings.CONVERSATIONS_CH_USER:
        other_user = conversation.users.exclude(user=user_from).first()
        user_wrapper = UserWrapper(user=other_user)
        url = user_wrapper.profile_url
        title = user_wrapper.get_full_name()

    elif conversation._type == settings.CONVERSATIONS_CH_PROJECT:
        project_uuid = conversation.uuid_related_object
        response = get_info_core_project(user_from, project_uuid)
        url = response['chatUrl']
        title = '{} ({})'.format(response['name'], conversation.name)

    elif conversation._type == settings.CONVERSATIONS_CH_EXO_PROJECT:
        project_uuid = conversation.uuid_related_object
        response = get_info_exo_project(user_from, project_uuid)
        url = response['chatUrl']
        title = '{} ({})'.format(response['name'], conversation.name)

    elif conversation._type == settings.CONVERSATIONS_CH_OPPORTUNITIES:
        opportunity_uuid = conversation.uuid_related_object
        response = get_info_opportunities(user_from, opportunity_uuid)
        url = response['chatUrl']
        title = response['title']
    return url, title
