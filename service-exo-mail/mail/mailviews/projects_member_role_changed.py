from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ProjectsMemberRoleChangedMailView(BaseMailView):
    """
    """
    template_name = 'mails/projects/member_role_changed.html'

    mandatory_mail_args = [
        'name',
        'user_name',
        'roles',
        'public_url',
    ]
    subject = _('Your role has changed: You are now acting as %(roles)s in %(name)s')
    section = 'projects'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Project Name]',
            'roles': ['ExO Head Coach', 'Observer'],
            'user_name': '[Name]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
