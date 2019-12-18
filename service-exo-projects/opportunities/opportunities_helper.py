import logging
import requests

from django.conf import settings


logger = logging.getLogger('service')
URL_CREATE_OPPORTUNITY_GROUP = 'api/group/'
URL_DETAIL_OPPORTUNITY_GROUP = 'api/group/{}/'
CH_GROUP_EXO_TEAM = 'E'


def _get_authorization():
    return {'USERNAME': settings.AUTH_SECRET_KEY}


def get_host():
    service_prefix = settings.SERVICE_OPPORTUNITIES_HOST
    host = settings.EXOLEVER_HOST + service_prefix
    return host


def get_data(advisor_request_settings, opportunity_group):
    return {
        'total': advisor_request_settings.total,
        'exo_role': advisor_request_settings.exo_role.code,
        'certification_required': advisor_request_settings.certification_required.code,
        'entity': advisor_request_settings.entity,
        'duration_unity': advisor_request_settings.duration_unity,
        'duration_value': advisor_request_settings.duration_value,
        'budgets': advisor_request_settings.budgets,
        'managers': list([user.uuid.__str__() for user in opportunity_group.managers]),
        'origin': CH_GROUP_EXO_TEAM,
        'related_uuid': opportunity_group.team.uuid.__str__(),
    }


def create_opportunity_group(advisor_request_settings, opportunity_group):
    data = get_data(advisor_request_settings, opportunity_group)
    url = get_host() + URL_CREATE_OPPORTUNITY_GROUP
    headers = _get_authorization()
    if settings.POPULATOR_MODE:
        return
    try:
        response = requests.post(url, json=data, headers=headers)
        assert response.status_code == requests.codes.created
        data = response.json()
        opportunity_group.group_uuid = data['uuid']
        opportunity_group.save()
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)


def update_opportunity_group(advisor_request_settings, opportunity_group):
    data = get_data(advisor_request_settings, opportunity_group)
    url = get_host() + URL_DETAIL_OPPORTUNITY_GROUP.format(
        opportunity_group.group_uuid.__str__())
    headers = _get_authorization()
    if settings.POPULATOR_MODE:
        return
    try:
        response = requests.put(url, json=data, headers=headers)
        assert response.status_code == requests.codes.ok
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)


def delete_opportunity_group(opportunity_group_uuid):
    url = get_host() + URL_DETAIL_OPPORTUNITY_GROUP.format(
        opportunity_group_uuid)
    headers = _get_authorization()
    if settings.POPULATOR_MODE:
        return
    try:
        requests.delete(url, headers=headers)
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)
