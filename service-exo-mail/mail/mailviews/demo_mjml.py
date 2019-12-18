# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class DemoMjmlMailView(BaseMailView):
    template_name = 'mails/demo_mjml.mjml'
    mandatory_mail_args = [
        'message',
    ]
    optional_mail_args = []
    section = 'mjml'

    def get_mock_data(self, optional=True):
        mock_data = {
            'message': faker.paragraph(),
        }

        return mock_data
