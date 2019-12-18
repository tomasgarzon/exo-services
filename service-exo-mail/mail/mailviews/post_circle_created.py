from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView
from ..mixins.circle_mixin import CircleMixin


class PostCircleCreatedMailView(CircleMixin, BaseMailView):
    template_name = 'mails/circles/post_circle_created.html'
    mandatory_mail_args = [
        'circle_name',
        'post_title',
        'post_content',
        'created_by_profile_picture',
        'created_by_name',
        'disable_notification_url',
    ]
    optional_mail_args = []
    subject = _('New post from %(created_by_name)s in %(circle_name)s')
    section = 'circles'
    config_param = 'new_post'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'post_title': '[Topic title]',
            'post_content': faker.text(),
            'circle_name': '[Circle name]',
            'created_by_name': faker.name(),
            'created_by_profile_picture': faker.image_url(settings.MEDIUM_IMAGE_SIZE, settings.MEDIUM_IMAGE_SIZE),
            'created_by_role': '[User Title]',
        })
        return mock_data
