# app imports
from ..mails import BaseMailView


class TestEmailMailView(BaseMailView):
    template_name = 'mails/test_email.html'
    mandatory_mail_args = []
    optional_mail_args = []
    section = 'test'
    subject = ''

    def get_mock_data(self, optional=True):
        mock_data = {}
        return mock_data
