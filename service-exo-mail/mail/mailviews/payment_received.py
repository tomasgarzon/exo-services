from django.utils.translation import ugettext_lazy as _

from ..mails import BaseMailView


class PaymentReceivedMailView(BaseMailView):
    template_name = 'mails/payments/payment_received.html'

    mandatory_mail_args = [
        'full_name',
        'concept',
    ]

    subject = _('Here is your invoice!')
    section = 'payments'

    def get_mock_data(self, optional=True):
        mock_data = {
            'full_name': '[Full Name]',
            'concept': '[Concept]',
        }
        return mock_data
