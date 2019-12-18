from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from utils.faker_factory import faker

from ..mails import BaseMailView


class NewOpportunityCreatedNotSignedAgreementMailView(BaseMailView):
    template_name = 'mails/opportunity/new_opportunity_created_not_signed_agreement.html'

    mandatory_mail_args = [
        'title',
        'created_by_profile_picture',
        'created_by_name',
        'created_by_user_title',
        'recipient_name',
        'public_url',
        'disable_notification_url',
    ]

    subject = _('New opportunity available!')
    section = 'opportunities'

    def get_mock_data(self, optional=True):
        mock_data = {
            'title': '[Role] for [Opportunity title]',
            'created_by_name': '[Created By User]',
            'created_by_profile_picture': faker.image_url(settings.DEFAULT_IMAGE_SIZE, settings.DEFAULT_IMAGE_SIZE),
            'created_by_user_title': '[User Title]',
            'recipient_name': '[Recipient Name]',
            'public_url': '/{}'.format(faker.uri_path()),
            'disable_notification_url': '/{}'.format(faker.uri_path()),
        }
        return mock_data
