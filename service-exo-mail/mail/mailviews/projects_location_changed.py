from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class ProjectsLocationChangedMailView(BaseMailView):
    """
    """
    template_name = 'mails/projects/project_location_changed.html'

    mandatory_mail_args = [
        'name',
        'user_name',
        'location',
        'public_url',
    ]

    subject = _('The location for %(name)s has changed')
    section = 'projects'

    def get_mock_data(self, optional=True):
        mock_data = {
            'name': '[Project Name]',
            'user_name': '[Name]',
            'location': '[New location]',
            'disable_notification_url': None,
            'public_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
