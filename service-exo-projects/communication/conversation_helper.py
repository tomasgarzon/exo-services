import logging
import requests

from django.conf import settings

from auth_uuid.utils.user_wrapper import UserWrapper
from auth_uuid.jwt_helpers import _build_jwt
from project.user_title_helper import get_user_title_in_project


logger = logging.getLogger('service')
URL_CREATE_CONVERSATION_GROUP = 'api/{}/conversations/create-group/'
URL_DETAIL_CONVERSATION_GROUP = 'api/{}/conversations/update/{}/'


def _get_authorization(user_from):
    token = _build_jwt(user_from)
    return {'Authorization': 'Bearer ' + token}


def get_host():
    service_prefix = settings.SERVICE_CONVERSATIONS_HOST
    host = settings.EXOLEVER_HOST + service_prefix
    return host


def add_user(user, project, team=None):
    user_wrapper = UserWrapper(user=user)
    return {
        'name': user_wrapper.get_full_name(),
        'profile_picture': user_wrapper.profile_picture[1][1],
        'short_title': get_user_title_in_project(project, user, team),
        'profile_url': user_wrapper.profile_url,
        'user_uuid': str(user.uuid),
    }


def create_group(group, user_from):
    groups = []
    group_data = {'name': group.get_name(), 'users': [], 'icon': group.get_icon()}
    for user in group.users.all():
        if group.is_for_team:
            user_data = add_user(user, group.project, group.team)
        else:
            user_data = add_user(user, group.project)
        group_data['users'].append(user_data)
    groups.append(group_data)
    data = {
        'user_from': str(user_from.uuid),
        'groups': groups,
        'group_type': 'S',  # CH_EXO_PROJECT
    }
    url = get_host() + URL_CREATE_CONVERSATION_GROUP.format(
        group.project.uuid.__str__())
    headers = _get_authorization(user_from)
    if settings.POPULATOR_MODE:
        return
    try:
        response = requests.post(url, json=data, headers=headers)
        assert response.status_code == requests.codes.ok
        data = response.json()[0]
        group.conversation_uuid = data['uuid']
        group.save()
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)


def update_group(group, user_from):
    data = {'name': group.get_name(), 'users': [], 'icon': group.get_icon()}
    for user in group.users.all():
        if group.is_for_team:
            user_data = add_user(user, group.project, group.team)
        else:
            user_data = add_user(user, group.project)
        data['users'].append(user_data)

    url = get_host() + URL_DETAIL_CONVERSATION_GROUP.format(
        group.project.uuid.__str__(),
        group.conversation_uuid.__str__())
    headers = _get_authorization(user_from)
    if settings.POPULATOR_MODE:
        return
    try:
        requests.put(url, json=data, headers=headers)
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)


def delete_group(group, user_from):
    url = get_host() + URL_DETAIL_CONVERSATION_GROUP.format(
        group.project.uuid.__str__(),
        group.conversation_uuid.__str__())
    headers = _get_authorization(user_from)
    if settings.POPULATOR_MODE:
        return
    try:
        requests.delete(url, headers=headers)
    except Exception as err:
        message = 'Exception: {}-{}'.format(err, url)
        logger.error(message)
