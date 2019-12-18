# app imports
from ..mails import BaseMailView


class BasicEmailMailView(BaseMailView):
    template_name = 'mails/basic_email.html'
    mandatory_mail_args = []
    optional_mail_args = []
    subject = 'OpenExO'
    section = 'basic'

    def get_mock_data(self, optional=True):
        mock_data = {}
        return mock_data
