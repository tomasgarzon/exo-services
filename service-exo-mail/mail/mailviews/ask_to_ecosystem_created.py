from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView
from ..mixins.circle_mixin import CircleMixin


class AskToEcosystemCreatedMailView(CircleMixin, BaseMailView):
    template_name = 'mails/ask_the_ecosystem/ask_to_ecosystem_created.html'
    mandatory_mail_args = [
        'post_content',
        'created_by_profile_picture',
        'created_by_name',
        'created_by_role',
        'disable_notification_url',
    ]
    optional_mail_args = []
    subject = _('New question from projects')
    section = 'ask_the_ecosystem'
    config_param = 'new_question_from_project'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'post_content': faker.text(),
            'circle_name': '[Circle name]',
            'created_by_name': faker.name(),
            'created_by_profile_picture': faker.image_url(settings.MEDIUM_IMAGE_SIZE, settings.MEDIUM_IMAGE_SIZE),
            'created_by_role': '[User Title]',
        })
        return mock_data
