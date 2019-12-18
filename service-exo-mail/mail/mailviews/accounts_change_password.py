# app imports
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class AccountsChangePasswordMailView(BaseMailView):
    template_name = 'mails/accounts_change_password.html'
    mandatory_mail_args = ['name', 'public_url']
    optional_mail_args = []
    subject = _('Password reset requested')
    section = 'password'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': faker.first_name(),
            'public_url': faker.uri_path(),
        }
        return mock_data
