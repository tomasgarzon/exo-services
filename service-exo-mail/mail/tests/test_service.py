from django.test import TestCase
from django.urls import reverse

from requests_toolbelt import MultipartEncoder
import mock
import json
from rest_framework import status
from unittest.mock import patch

from utils.faker_factory import faker


class TestServiceTestCase(TestCase):

    def setUp(self):
        super().setUp()

    @patch('mail.handlers.mail_handler.send_mail')
    @patch(
        'auth_uuid.middleware.AuthenticationMiddleware.process_request',
        mock.MagicMock(return_value=None))
    def test_send_mail(self, mock_send_mail_handler):
        # PREPARE DATA
        template = "accounts_change_password"
        url_reverse = reverse('api:mail-list')
        params = {
            "name": faker.name(),
            "public_url": faker.url(),
            "recipients": [faker.email()],
        }
        data = {
            "template": template,
            "params": json.dumps(params),
            "lang": "en",
        }
        m = MultipartEncoder(fields=data)
        # DO ACTION
        response = self.client.post(url_reverse, data=m.to_string(), content_type=m.content_type)
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_send_mail_handler.called)

    @patch(
        'auth_uuid.middleware.AuthenticationMiddleware.process_request',
        mock.MagicMock(return_value=None))
    def test_get_config_param_mailview(self):
        # PREPARE DATA
        template = "post_circle_created"
        url_reverse = reverse('api:config-list')
        output_config_param = 'new_post'
        data = {
            "template": template,
        }

        # DO ACTION
        response = self.client.post(url_reverse, data=data, content_type='application/json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('config'), output_config_param)
