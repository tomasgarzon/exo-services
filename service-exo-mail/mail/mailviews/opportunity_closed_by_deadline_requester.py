from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class OpportunityClosedByDeadlineRequesterMailView(BaseMailView):
    """
    """
    template_name = 'mails/opportunity/opportunity_closed_by_deadline_requester.html'

    mandatory_mail_args = [
        'title',
        'created_by_name',
        'public_url',
    ]

    subject = _('Opportunity expired')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        mock_data = {
            'title': '[Role] for [Project Name]',
            'created_by_name': '[SDM Name]',
            'disable_notification_url': None,
            'comment': faker.text(),
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
