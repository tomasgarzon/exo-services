from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class MarketplaceServiceRequestMailView(BaseMailView):
    template_name = 'mails/marketplace/service_request.html'
    mandatory_mail_args = [
        'name',
        'email',
        'company',
        'position',
        'participant',
        'motivation',
        'employees',
        'initiatives',
        'goal',
        'book',
        'comment',
    ]
    optional_mail_args = []
    subject = _('New Service Request')
    section = 'marketplace'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'name': faker.name(),
            'email': faker.email(),
            'company': '[company]',
            'position': '[position]',
            'participant': '[participant]',
            'motivation': '[motivation]',
            'employees': '[employees]',
            'initiatives': '[initiatives]',
            'goal': '[goal]',
            'book': faker.boolean(),
            'comment': '[comment]',
        })
        return mock_data
