# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class BaseConsultantValidationMailView(BaseMailView):
    template_name = ''
    mandatory_mail_args = ['user_name', 'public_url']
    optional_mail_args = ['description']

    def get_mock_data(self, optional=True):
        mock_data = {
            'user_name': '[[Consultant Short Name]]',
            'public_url': '/' + faker.uri_path(),
            'user_in_waiting_list': faker.boolean()
        }
        return mock_data
