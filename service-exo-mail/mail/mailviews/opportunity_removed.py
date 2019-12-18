from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunityRemovedMailView(BaseMailView):
    """
    """
    template_name = 'mails/opportunity/opportunity_removed.html'

    mandatory_mail_args = [
        'title',
        'applicant_name',
        'created_by_name',
        'public_url',
    ]

    subject = _('Opportunity deleted')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        mock_data = {
            'title': '[Role] for [Project Name]',
            'applicant_name': '[EM Name]',
            'created_by_name': '[SDM Name]',
            'disable_notification_url': None,
            'comment': faker.text(),
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
