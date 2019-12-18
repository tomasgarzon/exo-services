import json
from mock import patch
from django.urls import reverse
from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from utils.mails.handlers import mail_handler
from utils.mock_mixins import MagicMockMixin


class TestAPIChangeUserPassword(
        UserTestMixin,
        MagicMockMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        self.create_user()

    @patch.object(mail_handler, 'send_mail')
    def test_email_sent_request_password_change(self, mock_email):
        # PREPARE DATA
        url = reverse('api:password-request')
        data = {'email': self.user.email}

        # DO ACTION
        response = self.client.post(url, data=data, type='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(recipients, [self.user.email])

    @patch.object(mail_handler, 'send_mail')
    def test_email_sent_multiple_email(self, mock_email):
        # PREPARE DATA
        new_email = faker.email()
        self.user.add_email_address(new_email.upper(), True)
        url = reverse('api:password-request')

        # DO ACTION
        response = self.client.post(
            url,
            data={'email': new_email},
            type='json',
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        recipients = self.get_mock_kwarg(mock_email, 'recipients')
        self.assertEqual(recipients[0], new_email)

    def test_request_password_invalid_email(self):
        """
        Try to request a new Password for a not registered user
        """
        url = reverse('api:password-request')

        # DO ACTION
        response = self.client.post(
            url,
            data={'email': faker.email()},
            type='json',
        )

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertTrue(
            'email' in json.loads(response.content.decode('utf-8')).keys(),
        )
        self.assertEqual(len(mail.outbox), 0)

    def test_request_password_valid_upper_email(self):
        """
        Try to request a new Password for a  registered user with wrong email
        """
        url = reverse('api:password-request')

        # DO ACTION
        response = self.client.post(
            url,
            data={'email': self.user.email.upper()},
            type='json',
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @patch.object(mail_handler, 'send_mail')
    def test_set_new_password(self, mock_email):
        """
        Set new password for User
        """
        self.client.post(
            reverse('api:password-request'),
            data={'email': self.user.email},
            type='json',
        )
        self.assertTrue(mock_email.called)
        token = self.get_mock_kwarg(mock_email, 'public_url').split('/')[3]
        new_password = faker.password()
        url = reverse('api:password-change')

        data = {
            'token': token,
            'new_password1': new_password,
            'new_password2': new_password,
        }

        # DO ACTION
        response = self.client.post(url, data, type='json')

        # ASSERTS
        self.user.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.user.check_password(new_password))

    def test_invalid_token_password_recover(self):
        """
        Test invalid token when setting the new User password
        """
        url = reverse('api:password-change')
        new_password = faker.password()
        data = {
            'token': faker.md5(),
            'new_password1': new_password,
            'new_password2': new_password,
        }

        # DO ACTION
        response = self.client.post(url, data, type='json')

        # ASSERTS
        self.assertTrue(self.client.login(username=self.user.email, password='123456'))
        self.assertTrue(response.exception)
        backend_errors = response.json()
        self.assertTrue('nonFieldErrors' in backend_errors.keys())
        self.assertTrue('Invalid token' in backend_errors.get('nonFieldErrors'))

    @patch.object(mail_handler, 'send_mail')
    def test_invalid_new_password(self, mock_email):
        # PREPARE DATA
        self.client.post(
            reverse('api:password-request'),
            data={'email': self.user.email},
            type='json',
        )

        self.assertTrue(mock_email.called)
        token = self.get_mock_kwarg(mock_email, 'public_url').split('/')[3]
        url = reverse('api:password-change')

        data = {
            'token': token,
            'new_password1': faker.password(),
            'new_password2': faker.password(),
        }

        # DO ACTION
        response = self.client.post(url, data, type='json')

        # ASSERTS
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('123456'))
        self.assertTrue(response.exception)
        self.assertTrue('newPassword2' in response.json().keys())
