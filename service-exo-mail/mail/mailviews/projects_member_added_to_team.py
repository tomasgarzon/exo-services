from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ProjectsMemberAddedToTeamMailView(BaseMailView):
    """
    """
    template_name = 'mails/projects/member_added_to_team.html'

    mandatory_mail_args = [
        'team_name',
        'user_name',
        'roles',
        'public_url',
    ]

    subject = _('Congratulations! You are now part of %(team_name)s as %(roles)s')
    section = 'projects'

    def get_mock_data(self, optional=True):
        mock_data = {
            'team_name': '[Team Name]',
            'roles': ['ExO Sprint Coach'],
            'user_name': '[Name]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
