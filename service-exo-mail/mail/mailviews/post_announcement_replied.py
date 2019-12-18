from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView
from ..mixins.circle_mixin import CircleMixin


class PostAnnouncementRepliedMailView(CircleMixin, BaseMailView):
    template_name = 'mails/circles/post_announcement_replied.html'
    mandatory_mail_args = [
        'short_name',
        'created_by_name',
        'created_by_profile_picture',
        'answer_content',
        'public_url',
        'disable_notification_url',
    ]
    optional_mail_args = []
    subject = _('New Reply to an Announcement')
    section = 'circles'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'short_name': '[Short name]',
            'created_by_name': '[Created By User]',
            'created_by_profile_picture': faker.image_url(settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE),
            'created_by_role': '[User Title]',
            'answer_content': '[Reply Comment]'
        })
        return mock_data
