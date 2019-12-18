from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class NewPaymentCreatedMailView(BaseMailView):
    template_name = 'mails/payments/new_payment_created.html'

    mandatory_mail_args = [
        'full_name',
        'concept',
        'detail',
        'amount',
        'currency',
        'public_url',
    ]

    subject = _('Payment Request from OpenExO')
    section = 'payments'

    def get_mock_data(self, optional=True):
        mock_data = {
            'full_name': '[Full Name]',
            'concept': '[Concept]',
            'detail': '[Detail]',
            'amount': '[Amount]',
            'currency': '[Currency]',
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
