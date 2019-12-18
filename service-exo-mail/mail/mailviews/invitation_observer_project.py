from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from utils.faker_factory import faker

from ..mails import BaseMailView


class InvitationObserverProjectMailView(BaseMailView):
    template_name = 'mails/invitation_observer_project.html'
    mandatory_mail_args = ['project_type', 'project_name', 'public_url']
    optional_mail_args = []
    subject = _(settings.BRAND_NAME + ' - Access invite')
    section = 'project'

    def get_mock_data(self, optional=True):
        project_name = faker.word()
        mock_data = {
            'project_type': '[Project_type]',
            'project_name': project_name,
            'public_url': '/{}'.format(faker.uri_path()),
        }

        return mock_data
