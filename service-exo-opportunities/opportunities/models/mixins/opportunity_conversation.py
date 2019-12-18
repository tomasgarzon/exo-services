import requests
import logging

from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt
from auth_uuid.utils.user_wrapper import UserWrapper

logger = logging.getLogger('service')


def add_user(user):
    if isinstance(user, dict):
        uuid = user['uuid'].__str__()
        user_wrapper = UserWrapper(uuid)
    else:
        user_wrapper = UserWrapper(user=user)
        uuid = user.uuid.__str__()
    return {
        'name': user_wrapper.get_full_name(),
        'profile_picture': user_wrapper.profile_picture[1][1],
        'short_title': user_wrapper.user_title,
        'profile_url': user_wrapper.profile_url,
        'user_uuid': uuid,
    }


def create_conversation(opportunity, users):
    user_from = users[-1]
    user_wrapper = UserWrapper(user=user_from)
    icon = user_wrapper.profile_picture[1][1]
    group_name = user_wrapper.get_full_name()
    users_to = [add_user(user) for user in users]
    return group_name, users_to, icon


class OpportunityConversationMixin():
    def get_info_for_start_conversation(self, user_from, user_to=None):
        users = []
        users.extend(self.admin_users)
        users.append(user_from)
        if user_to:
            users.append(user_to)
        return create_conversation(self, users)

    def get_unread_messages(self, user_from):
        num_messages = None

        token = _build_jwt(user_from)
        host = settings.EXOLEVER_HOST + settings.SERVICE_CONVERSATIONS_HOST
        url = host + 'api/{}/conversations/total/'.format(self.uuid.__str__())
        headers = {'Authorization': 'Bearer ' + token}

        if not settings.POPULATOR_MODE:
            try:
                response = requests.get(url, headers=headers)
                num_messages = response.json()
            except Exception as err:
                message = 'requests.Exception: {}'.format(err)
                logger.error(message)

        return num_messages
