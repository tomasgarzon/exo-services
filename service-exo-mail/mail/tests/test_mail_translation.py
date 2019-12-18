from django.conf import settings
from django.test import TestCase
from django.utils import translation

from unittest.mock import patch

from utils.faker_factory import faker

from ..handlers import mail_handler


class TestEmailLanguageSelector(TestCase):

    def setUp(self):
        super().setUp()
        # MaYbe other test has activated LANGUAGE_EN and is not the Django default
        translation.activate(settings.LANGUAGE_CODE)

    @patch('mail.sender.send_email')
    @patch('mail.handlers.mail_handler.activate_language')
    def test_determine_email_language_called(self, mock_send_email, mock_activate_language):
        # PREPARE DATA
        template = 'test_email'
        domain = ''
        data = {
            'recipients': [faker.email()]
        }

        # DO ACTION
        mail_handler.send_mail(domain, template, data)

        # ASSERTS
        self.assertEqual(mock_activate_language.call_count, 1)
