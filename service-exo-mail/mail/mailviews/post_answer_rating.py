import random

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView
from ..mixins.circle_mixin import CircleMixin


class PostAnswerRatingMailView(CircleMixin, BaseMailView):
    template_name = 'mails/circles/post_answer_rating.html'
    mandatory_mail_args = [
        'post_title',
        'answer_content',
        'created_by_name',
        'created_by_profile_picture',
    ]
    optional_mail_args = []
    subject = _('New rating')
    section = 'circles'

    def get_mock_data(self, optional=True):
        mock_data = super().get_mock_data()

        mock_data.update({
            'post_title': '[Topic title]',
            'answer_content': faker.text(),
            'answer_rating': random.randint(1, 5),
            'created_by_name': faker.name(),
            'created_by_profile_picture': faker.image_url(settings.MEDIUM_IMAGE_SIZE, settings.MEDIUM_IMAGE_SIZE),
            'created_by_role': '[User Title]',
        })
        return mock_data
