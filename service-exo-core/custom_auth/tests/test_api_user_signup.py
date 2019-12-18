import uuid

from django.urls import reverse
from django.contrib.auth import get_user_model

from unittest.mock import patch

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin


class UserSignUpTest(
        UserTestMixin, SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()

    def generate_fake_data(self):
        return {
            'uuid': uuid.uuid4().__str__(),
            'short_name': faker.first_name(),
            'full_name': faker.name(),
            'email': faker.email(),
            'password': faker.password(),
            'is_active': True,
            'is_superuser': False,
            'is_staff': False,
        }

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_signup_ok(self, mock_email):
        # PREPARE DATA
        data = self.generate_fake_data()
        url = reverse('api:accounts:signup-auth')
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(mock_email.called)
        user = get_user_model().objects.get(uuid=data.pop('uuid'))
        self.assertTrue(user.check_password(data.pop('password')))
        self.assertTrue(response.json()['created'])
        for key, value in data.items():
            self.assertEqual(
                getattr(user, key),
                value)

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_signup_previous_user(self, mock_email):
        # PREPARE DATA
        user = FakeUserFactory.create()
        data = self.generate_fake_data()
        data['email'] = user.email
        url = reverse('api:accounts:signup-auth')
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(mock_email.called)
        self.assertFalse(
            get_user_model().objects.filter(uuid=data.get('uuid')).exists())
        data = response.json()
        self.assertEqual(
            user.pk, data['pk'])
        self.assertEqual(
            user.uuid.__str__(), data['uuid'])
        self.assertFalse(data['created'])
