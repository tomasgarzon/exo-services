from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ProjectsMemberRemovedMailView(BaseMailView):
    """
    """
    template_name = 'mails/projects/member_removed_from_project_launched.html'

    mandatory_mail_args = [
        'name',
        'user_name',
        'roles',
        'public_url',
    ]

    subject = _('You are no longer %(roles)s in %(name)s')
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
