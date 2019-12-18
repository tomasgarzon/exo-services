from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ProjectsStartChangedMailView(BaseMailView):
    """
    """
    template_name = 'mails/projects/project_start_changed.html'

    mandatory_mail_args = [
        'name',
        'user_name',
        'start_date',
        'public_url',
    ]

    subject = _('%(name)s starts on %(start_date)s')
    section = 'projects'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Week/Project]',
            'user_name': '[Name]',
            'start_date': '[Start date]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
