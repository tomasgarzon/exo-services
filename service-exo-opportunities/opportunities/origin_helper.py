import logging

from django.conf import settings

import requests


logger = logging.getLogger('service')


def _get_headers():
    return {'USERNAME': settings.AUTH_SECRET_KEY}


def get_project_info(related_uuid):
    URL = '/api/project/admin-project/filter_by_team/?team={}'
    headers = _get_headers()
    url = URL.format(related_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def get_exo_project_info(related_uuid):
    URL = '{}api/admin-project/filter_by_team/?team={}'
    headers = _get_headers()
    url = URL.format(
        settings.SERVICE_PROJECTS_HOST, related_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def get_exo_project_info_by_uuid(related_uuid):
    URL = '{}api/admin-project/{}/'
    headers = _get_headers()
    url = URL.format(
        settings.SERVICE_PROJECTS_HOST, related_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)


def get_event_info_by_uuid(related_uuid):
    URL = '{}api/event/{}/'
    headers = _get_headers()
    url = URL.format(
        settings.SERVICE_EVENTS_HOST, related_uuid.__str__())
    try:
        response = requests.get(
            settings.EXOLEVER_HOST + url,
            headers=headers)
        assert response.status_code == requests.codes.ok
        return response.json()
    except Exception as e:
        logger.error(e)
        logger.error(settings.EXOLEVER_HOST + url)
