from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class VerificationEmailAddressMailView(BaseMailView):
    template_name = 'mails/user/verification_email_address.html'
    mandatory_mail_args = ['user_name', 'public_url']
    optional_mail_args = []

    subject = _('Email Address Verification')
    section = 'user'

    def get_mock_data(self, optional=True):
        mock_data = {
            'user_name': '[[consultant_short_name]]',
            'public_url': faker.uri_path(),
        }
        return mock_data
