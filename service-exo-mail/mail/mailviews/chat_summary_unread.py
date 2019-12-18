import random

from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ChatSummaryUnreadMailView(BaseMailView):

    template_name = 'mails/chat/summary.html'

    mandatory_mail_args = [
        'conversations',
        'name',
        'total',
    ]

    subject = _('%(period)s unread messages')
    section = 'chat'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Name]',
            'disable_notification_url': None,
            'conversations': [
                {
                    'total': faker.pyint(),
                    'title': random.choice([
                        'messages from [User Name]',
                        'messages related to opportunity [opportunity name]',
                        'messages related to the project [project name]']),
                    'user_from_full_name': '[User Name]',
                    'message': faker.text(),
                    'url': '/{}'.format(faker.uri_path()),
                } for _ in range(5)
            ],
            'total': faker.pyint(),
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
