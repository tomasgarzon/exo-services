from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ProjectsMemberLaunchMailView(BaseMailView):
    """
    """
    template_name = 'mails/projects/member_launch.html'

    mandatory_mail_args = [
        'name',
        'user_name',
        'roles',
        'start_date',
        'public_url',
    ]

    subject = _('You will be participating in %(name)s as %(roles)s')
    section = 'projects'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Project Name]',
            'roles': ['ExO Head Coach', 'Observer'],
            'user_name': '[Name]',
            'start_date': '[Start date]',
            'message': '[Message]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
