from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from utils.faker_factory import faker

from ..mails import BaseMailView


class ChatFirstMessageMailView(BaseMailView):
    """
    """
    template_name = 'mails/chat/first_message.html'

    mandatory_mail_args = [
        'user_from_full_name',
        'user_from_title',
        'user_from_profile_picture',
        'title',
        'message',
        'public_url',
    ]

    subject = _('New chat conversation')
    section = 'chat'
    config_param = 'new_conversation'

    def get_mock_data(self, optional=True):
        mock_data = {
            'title': '[user-name] started a new conversation [related to <opportunity-name>]|<project-name>]',
            'user_from_full_name': '[User From name]',
            'user_from_title': '[User from title]',
            'user_from_profile_picture': faker.image_url(settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE),
            'disable_notification_url': None,
            'message': faker.text(),
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
