from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunitySummaryNotSignedAgreementMailView(BaseMailView):

    template_name = 'mails/opportunity/opportunity_daily_summary_not_signed_agreement.html'

    mandatory_mail_args = [
        'roles',
        'name',
        'public_url',
        'total',
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
                } for _ in range(4)
            ],
            'total': faker.pyint(),
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
