# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class EmailTeamMailView(BaseMailView):
    template_name = 'mails/email_team.html'
    mandatory_mail_args = [
        'message', 'name', 'role_name', 'project_name', 'subject', 'public_url'
    ]
    optional_mail_args = []
    section = 'project'

    def get_subject(self, **kwargs):
        return kwargs.get('subject')

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': faker.word(),
            'project_name': faker.word(),
            'role_name': faker.word(),
            'message': faker.paragraph(),
            'subject': '[Subject]',
            'public_url': '/{}'.format(faker.uri_path()),
        }

        return mock_data
