from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ReminderAdvisorTomorrowQaSessionMailView(BaseMailView):
    template_name = 'mails/swarm/reminder_advisor_qa_session.html'
    mandatory_mail_args = [
        'short_name',
        'project_name',
        'location',
        'timezone_utc',
        'timezone_name',
        'start_at',
        'one_day',
        'disable_notification_url',
        'my_jobs_url',
    ]
    optional_mail_args = []
    section = 'swarm'
    subject = _('Swarm Session Tomorrow')
    config_param = 'reminder_tomorrow'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'short_name': '[Shot name]',
            'location': '[Project location]',
            'project_name': '[Client Name]',
            'timezone_name': 'Europe/Madrid',
            'timezone_utc': '+1.00',
            'start_at': '2017-08-03T10:00:00.000000',
            'one_day': faker.boolean(),
            'disable_notification_url': '/{}'.format(faker.uri_path()),
            'my_jobs_url': '/ecosystem/jobs/',
        })
        return mock_data
