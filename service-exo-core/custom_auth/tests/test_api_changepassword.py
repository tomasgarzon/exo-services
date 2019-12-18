import json
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model

from rest_framework import status

from utils.faker_factory import faker
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin

from .test_password_mixin import PasswordTestMixin


class TestAPIChangeUserPassword(
    UserTestMixin,
    SuperUserTestMixin,
    DjangoRestFrameworkTestCase,
    PasswordTestMixin
):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.create_user()

    def test_email_sent_user_not_signup(self):
        # PREPARE DATA
        url = reverse('api:accounts:password:request')
        email = faker.email()
        user, _ = get_user_model().objects.get_or_create(
            email=email,
            defaults={'short_name': faker.first_name()},
            user_from=self.user,
        )
        data = {'email': email}

        # DO ACTION
        response = self.client.post(url, data=data, type='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], user.email)

    def test_email_sent_request_password_change(self):
        # PREPARE DATA
        url = reverse('api:accounts:password:request')
        data = {'email': self.user.email}

        # DO ACTION
        response = self.client.post(url, data=data, type='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], self.user.email)

    def test_email_sent_multiple_email(self):
        # PREPARE DATA
        new_email = faker.email()
        self.user.add_email_address(new_email.upper(), True)
        url = reverse('api:accounts:password:request')

        # DO ACTION
        response = self.client.post(
            url,
            data={'email': new_email},
            type='json',
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to[0], new_email)

    def test_request_password_invalid_email(self):
        """
        Try to request a new Password for a not registered user
        """
        url = reverse('api:accounts:password:request')

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
        url = reverse('api:accounts:password:request')

        # DO ACTION
        response = self.client.post(
            url,
            data={'email': self.user.email.upper()},
            type='json',
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_set_new_password(self):
        """
        Set new password for User
        """
        # TO DO: checkear params y ver que llega token
        self.client.post(
            reverse('api:accounts:password:request'),
            data={'email': self.user.email},
            type='json',
        )
        email = mail.outbox[0]
        token = self.get_token_from_email(email.body)
        new_password = faker.password()
        url = reverse('api:accounts:password:change')

        data = {
            'token': token,
            'new_password1': new_password,
            'new_password2': new_password,
        }

        # DO ACTION
        response = self.client.post(url, data, type='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.client.login(username=self.user.email, password=new_password))

    def test_invalid_token_password_recover(self):
        """
        Test invalid token when setting the new User password
        """
        url = reverse('api:accounts:password:change')
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
        backend_errors = json.loads(response.content.decode('utf-8'))
        self.assertTrue('non_field_errors' in backend_errors.keys())
        self.assertTrue('Invalid token' in backend_errors.get('non_field_errors'))

    def test_invalid_new_password(self):
        # PREPARE DATA
        self.client.post(
            reverse('api:accounts:password:request'),
            data={'email': self.user.email},
            type='json',
        )

        email = mail.outbox[0]
        token = self.get_token_from_email(email.body)
        url = reverse('api:accounts:password:change')

        data = {
            'token': token,
            'new_password1': faker.password(),
            'new_password2': faker.password(),
        }

        # DO ACTION
        response = self.client.post(url, data, type='json')

        # ASSERTS
        self.assertTrue(self.client.login(username=self.user.email, password='123456'))
        self.assertTrue(response.exception)
        self.assertTrue('new_password2' in json.loads(response.content.decode('utf-8')).keys())
