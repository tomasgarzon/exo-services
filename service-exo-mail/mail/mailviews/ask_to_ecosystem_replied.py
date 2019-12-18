from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker


from ..mails import BaseMailView
from ..mixins.circle_mixin import CircleMixin


class AskToEcosystemRepliedMailView(CircleMixin, BaseMailView):
    template_name = 'mails/ask_the_ecosystem/ask_to_ecosystem_replied.html'
    mandatory_mail_args = [
        'created_by_name',
        'created_by_profile_picture',
        'answer_content',
        'public_url',
        'disable_notification_url',
    ]
    optional_mail_args = []
    subject = _('New Answer to your Question')
    section = 'ask_the_ecosystem'
    config_param = 'new_answer'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'created_by_name': faker.name(),
            'created_by_profile_picture': faker.image_url(settings.MEDIUM_IMAGE_SIZE, settings.MEDIUM_IMAGE_SIZE),
            'created_by_role': '[User Title]',
            'answer_content': faker.text(),
        })
        return mock_data
