from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class EcosystemWeeklySummaryMailView(BaseMailView):
    template_name = 'mails/circles/ecosystem_weekly_summary.html'
    mandatory_mail_args = [
        'circles',
        'new_announcements',
        'new_questions',
    ]
    optional_mail_args = []
    subject = _('Weekly update')
    section = 'circles'
    config_param = 'weekly_update'

    def get_mock_data(self, optional=True):
        mock_data = {}
        circles = [
            {
                'name': '[Circle Name 1]',
                'new_topics': faker.random_digit(),
                'new_replies': faker.random_digit(),
                'code': 'T',
            },
            {
                'name': '[Circle Name 2]',
                'new_topics': faker.random_digit(),
                'new_replies': faker.random_digit(),
                'code': 'C',
            },
        ]
        mock_data.update({
            'circles': circles,
            'new_announcements': faker.random_digit(),
            'new_questions': faker.random_digit(),
            'public_url': '/{}'.format(faker.uri_path()),
            'disable_notification_url': '/{}'.format(faker.uri_path()),
        })
        return mock_data
