# app imports
from utils.faker_factory import faker

from ..mails import BaseMailView


class InvitationNetworkMemberMailView(BaseMailView):
    template_name = 'mails/invitation_network_member.html'
    mandatory_mail_args = ['public_url']
    optional_mail_args = []
    subject = 'You have been invited to join ExO-Works'
    section = 'registration'

    def get_mock_data(self, optional=True):
        mock_data = {
            'public_url': '/' + faker.uri_path(),
        }
        return mock_data
