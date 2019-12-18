from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunitySummaryMailView(BaseMailView):

    template_name = 'mails/opportunity/opportunity_daily_summary.html'

    mandatory_mail_args = [
        'roles',
        'name',
        'public_url',
        'total',
        'other_total',
    ]

    subject = _('%(total)s new opportunities in the OpenExO Marketplace')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Name]',
            'disable_notification_url': None,
            'roles': [
                {
                    'total': faker.pyint(), 'name': '[Role Name]',
                    'opportunities': [{
                        'title': '[Title]', 'entity': 'Client Name', 'description': '[Description]',
                        'url': '/{}'.format(faker.uri_path()), 'deadline': '14 november 2019'} for _ in range(3)
                    ]
                } for _ in range(2)
            ],
            'total': faker.pyint(),
            'other_total': faker.pyint(),
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
