from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ReminderParticipantTomorrowQaSessionMailView(BaseMailView):
    template_name = 'mails/swarm/reminder_participant_qa_session.html'
    mandatory_mail_args = [
        'short_name',
        'location',
        'timezone_utc',
        'timezone_name',
        'start_at',
        'public_url',
        'one_day',
        'disable_notification_url',
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
            'timezone_name': 'Europe/Madrid',
            'timezone_utc': '+1.00',
            'start_at': '2017-08-03T10:00:00.000000',
            'public_url': '/{}'.format(faker.uri_path()),
            'one_day': faker.boolean(),
            'disable_notification_url': '/{}'.format(faker.uri_path()),
        })
        return mock_data
