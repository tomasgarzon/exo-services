from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class QASessionSummaryMailView(BaseMailView):
    template_name = 'mails/swarm/qa_session_summary.html'
    mandatory_mail_args = [
        'short_name',
        'project_name',
        'location',
        'timezone_utc',
        'timezone_name',
        'start_at',
        'total_questions',
        'your_answers',
        'rating',
        'disable_notification_url',
        'public_url',
    ]
    optional_mail_args = []
    section = 'swarm'
    subject = _('Swarm Session Summary')
    config_param = 'session_summary'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'short_name': '[Shot name]',
            'location': '[Project location]',
            'project_name': '[Client Name]',
            'timezone_name': 'Europe/Madrid',
            'timezone_utc': '+1.00',
            'start_at': '2017-08-03T10:00:00.000000',
            'public_url': '/{}'.format(faker.uri_path()),
            'total_questions': faker.pyint(),
            'your_answers': faker.pyint(),
            'rating': 4,
            'disable_notification_url': '/{}'.format(faker.uri_path()),
        })
        return mock_data
