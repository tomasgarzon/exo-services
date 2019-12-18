import logging
import requests
from django.conf import settings

from custom_auth.helpers import UserProfileWrapper
from custom_auth.jwt_helpers import _build_jwt

from .tasks import NewConversationUserTask


logger = logging.getLogger('service')

URL_CREATE_CONVERSATION_GROUP = 'api/conversations/create-group/'
CHAT_NEW_CONVERSATION = 'new_conversation'


def add_user(user):
    return {
        'name': user.get_full_name(),
        'profile_picture': user.profile_picture.get_thumbnail_url(48, 48),
        'short_title': user.user_title,
        'profile_url': UserProfileWrapper(user).profile_slug_url,
        'user_uuid': user.uuid.__str__(),
    }


def create_conversation(users):
    user_from = users[-1]
    icon = user_from.profile_picture.get_thumbnail_url(48, 48)
    group_name = user_from.get_full_name()
    users_to = [add_user(user) for user in users]
    return group_name, users_to, icon


def get_info_for_start_conversation(user_from, user_to):
    users = []
    users.append(user_from)
    if user_to:
        users.append(user_to)
    return create_conversation(users)


def _get_authorization(user_from):
    token = _build_jwt(user_from)
    return {'Authorization': 'Bearer ' + token}


def get_host():
    return '{}{}{}'.format(
        settings.EXOLEVER_HOST,
        settings.SERVICE_CONVERSATIONS_HOST,
        URL_CREATE_CONVERSATION_GROUP)


def start_conversation(user_from, user_to, files=[], message=''):
    logging.info('User 1 to 1 {}, creating conversation'.format(user_from.id))

    group_name, users, icon = get_info_for_start_conversation(
        user_from,
        user_to=user_to)
    groups = [
        {'name': group_name, 'users': users, 'icon': icon}
    ]
    headers = _get_authorization(user_from)
    url = get_host()
    if not url:
        return None

    data = {
        'user_from': str(user_from.uuid),
        'groups': groups,
        'group_type': 'U',  # CH_USER
        'message': message,
        'files': files,
    }
    if settings.POPULATOR_MODE and not settings.TEST_MODE:
        return None
    try:
        response = requests.post(url, json=data, headers=headers)
        assert response.status_code == requests.codes.ok
        NewConversationUserTask().s(
            user_to_pk=user_to.pk,
            user_from_pk=user_from.pk,
            message=message).apply_async()
    except AssertionError:
        message = 'Exception: {}-{}'.format(response.content, url)
        logger.error(message)
