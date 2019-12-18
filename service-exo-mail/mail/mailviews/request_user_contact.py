from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class RequestUserContactMailView(BaseMailView):
    template_name = 'mails/user/request_user_contact.html'
    mandatory_mail_args = [
        'short_name',
        'requester_name',
        'requester_profile_picture',
        'user_title',
        'requester_profile_url',
        'requester_short_name',
        'requester_email',
        'comment',
    ]
    optional_mail_args = []
    subject = _('Contact request')
    section = 'ecosystem'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'short_name': '[Short name]',
            'requester_name': '[Requester full name]',
            'requester_short_name': '[Requester name]',
            'requester_profile_picture': faker.image_url(settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE),
            'user_title': 'Consultant, Coach, Speaker',
            'requester_email': faker.email(),
            'requester_profile_url': '/{}'.format(faker.uri_path()),
            'comment': '[Comment]',
        })
        return mock_data
