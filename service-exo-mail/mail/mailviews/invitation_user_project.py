from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from utils.faker_factory import faker

from ..mails import BaseMailView


class InvitationUserProjectMailView(BaseMailView):
    template_name = 'mails/invitation_user_project.html'
    mandatory_mail_args = [
        'project_name', 'project_type', 'team_name', 'public_url'
    ]
    optional_mail_args = []
    subject = _(settings.BRAND_NAME + ' - Team participant invite')
    section = 'project'

    def get_mock_data(self, optional=True):
        mock_data = {
            'team_name': '[Team Name]',
            'project_name': '[Project Name]',
            'project_type': '[Project type]',
            'public_url': '/{}'.format(faker.uri_path()),
        }

        return mock_data
