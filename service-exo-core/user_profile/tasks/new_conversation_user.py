import celery
import logging
from django.contrib.auth import get_user_model
from django.conf import settings

from utils.mail import handlers
from custom_auth.helpers import UserProfileWrapper


logger = logging.getLogger('celery-task')
MAIL_CHAT_FIRST_MESSAGE = 'chat_first_message'


class NewConversationUserTask(celery.Task):
    name = 'NewConversationUserTask'

    def run(self, *args, **kwargs):
        try:
            user_from = get_user_model().objects.get(
                pk=kwargs.get('user_from_pk'))
        except get_user_model().DoesNotExist:
            logger.error('User from does not exist')
            raise Exception()

        try:
            user_to = get_user_model().objects.get(
                pk=kwargs.get('user_to_pk'))
        except get_user_model().DoesNotExist:
            logger.error('Other User created does not exist')
            raise Exception()

        data = {}
        data['user_from_full_name'] = user_from.get_full_name()
        data['user_from_title'] = user_from.user_title
        data['user_from_profile_picture'] = user_from.profile_picture.get_thumbnail_url()
        data['title'] = '{} started a new conversation'.format(
            user_from.get_full_name())
        data['disable_notification_url'] = UserProfileWrapper(user_to).account_url
        data['message'] = kwargs.get('message')
        data['public_url'] = settings.FRONTEND_MESSAGES_PAGE
        data['recipients'] = [user_to.email]
        handlers.mail_handler.send_mail(
            MAIL_CHAT_FIRST_MESSAGE, **data)
