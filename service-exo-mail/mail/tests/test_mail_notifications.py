import mock
import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from requests_toolbelt import MultipartEncoder
from rest_framework import status
from unittest.mock import patch

from utils.faker_factory import faker


def mocked_requests(*args, **kwargs):

    class MockResponse:
        def __init__(self, status_code=status.HTTP_200_OK, *args, **kwargs):
            self.status_code = status_code
            self.ok = True

    return MockResponse(**kwargs)


class TestEmailNotificationSelector(TestCase):

    @patch(
        'auth_uuid.middleware.AuthenticationMiddleware.process_request',
        mock.MagicMock(return_value=None)
    )
    @patch('requests.put', side_effect=mocked_requests)
    def test_send_mail_without_notify_webhook(self, request_mock):
        # PREPARE DATA
        template = 'accounts_change_password'
        url_reverse = reverse('api:mail-list')
        params = {
            'name': faker.name(),
            'public_url': faker.url(),
            'recipients': [faker.email()],
        }
        data = {
            'template': template,
            'params': json.dumps(params),
            'lang': 'en',
        }

        m = MultipartEncoder(fields=data)

        # DO ACTION
        with self.settings(
                EMAIL_BACKEND='mail.backend.StoreBackend',
                EXOMAILER_STORAGE='django.core.files.storage.FileSystemStorage',
                EXOMAILER_STORAGE_OPTIONS={}):
            self.client.post(
                url_reverse,
                data=m.to_string(),
                content_type=m.content_type,
            )

        # ASSERTS
        self.assertFalse(request_mock.called)
        self.assertIsNone(request_mock.call_args)

    @patch(
        'auth_uuid.middleware.AuthenticationMiddleware.process_request',
        mock.MagicMock(return_value=None)
    )
    @patch('requests.put', side_effect=mocked_requests)
    def test_send_mail_with_notify_webhook(self, request_mock):
        # PREPARE DATA
        template = 'accounts_change_password'
        url_reverse = reverse('api:mail-list')
        notify_webhook_url = faker.url()
        params = {
            'name': faker.name(),
            'public_url': faker.url(),
            'recipients': [faker.email()],
            'notify_webhook': notify_webhook_url,
        }
        data = {
            'template': template,
            'params': json.dumps(params),
            'lang': 'en',
        }

        m = MultipartEncoder(fields=data)

        # DO ACTION
        with self.settings(
                EMAIL_BACKEND='mail.backend.StoreBackend',
                EXOMAILER_STORAGE='django.core.files.storage.FileSystemStorage',
                EXOMAILER_STORAGE_OPTIONS={}):
            self.client.post(
                url_reverse,
                data=m.to_string(),
                content_type=m.content_type,
            )

        # ASSERTS
        requested_url, request_params = request_mock.call_args
        self.assertTrue(request_mock.called)
        self.assertEqual(requested_url[0], notify_webhook_url)
        self.assertEqual(
            request_params.get('data').get('email_status'),
            settings.MAIL_NOTIFY_WEBHOOK_STATUS_OK
        )
        email_url = '{}{}'.format(
            settings.DOMAIN_NAME,
            reverse('mail:inbox-message', kwargs={'pk': 9999})
        ).replace('9999/', '')
        email_url_sent = request_params.get('data').get('email_url')
        self.assertTrue(email_url in email_url_sent)
