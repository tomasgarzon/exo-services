from django.urls import reverse
from django.conf import settings

from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker


class InvitationPreviewTest(DjangoRestFrameworkTestCase):

    def test_preview(self):
        # PREPARE DATA
        invitation_type = settings.CONSULTANT_VALIDATION_AGREEMENT
        data = {
            'validation_type': invitation_type,
            'name': faker.first_name(),
            'custom_text': faker.text(),
        }
        url = reverse('api:invitation:preview-email')

        # DO ACTION
        response = self.client.get(url, data=data, format='json')

        # ASSERTS
        # mail_handler.send_mail is always mocked in test runner
        self.assertIsNone(response.data)
