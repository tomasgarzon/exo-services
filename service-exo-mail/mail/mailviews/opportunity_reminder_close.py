from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunityReminderCloseMailView(BaseMailView):
    """
    """
    template_name = 'mails/opportunity/opportunity_reminder_close.html'

    mandatory_mail_args = [
        'title',
        'created_by_name',
        'duedate_timedelta',
        'duedate',
        'public_url',
    ]

    section = 'opportunities'
    subject = '%(duedate_timedelta)s until opportunity closure'

    def get_mock_data(self, optional=True):
        mock_data = {
            'title': '[Role Name] for [Project Name]',
            'created_by_name': '[SDM Name]',
            'duedate_timedelta': '3 days',
            'duedate': '[May 29, 12AM]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
