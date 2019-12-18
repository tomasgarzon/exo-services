from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin


class TestAPIAuthUser(
        UserTestMixin,
        APITestCase
):

    def setUp(self):
        self.create_super_user()
        self.create_user()

    def test_login(self):
        user_pwd = '123456'
        url = reverse('api:rest_login')
        data = {
            'username': self.super_user.email,
            'password': user_pwd,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data['url'], '/')
        url = reverse('api:me')
        token = response.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        response = self.client.get(url, format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_logout(self):
        user_pwd = '123456'
        url = reverse('api:rest_login')
        data = {
            'username': self.super_user.email,
            'password': user_pwd,
        }
        response = self.client.post(url, data=data, format='json')
        url = reverse('api:rest_logout')
        response = self.client.get(url, format='json')
        self.assertTrue(status.is_success(response.status_code))
        url = reverse('api:me')
        response = self.client.get(url, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

    def test_login_upper(self):
        user_pwd = '123456'
        url = reverse('api:rest_login')
        data = {
            'username': self.super_user.email.upper(),
            'password': user_pwd,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))

    def test_login_wrong(self):
        user_pwd = '123456'

        # ##
        # Invalid User
        # ##
        url = reverse('api:rest_login')
        data = {
            'username': faker.email(),
            'password': user_pwd,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

        # ##
        # Invalid password
        # ##
        data = {
            'username': self.super_user.email,
            'password': faker.word(),
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

    def test_login_email_address(self):
        """
            Login with a VALIDATED alternative EmailAddress
        """

        user_pwd = '123456'
        url = reverse('api:rest_login')

        # ##
        # Not verified email tries to login
        # ##
        new_email = self.user.add_email_address(faker.email())
        self.assertTrue(self.user.check_password(user_pwd))
        data = {
            'username': new_email.email,
            'password': user_pwd,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

        # ##
        # Already VERIFIED email login
        # ##

        new_email.verified_at = timezone.now()
        new_email.save()

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))

        # ##
        # Admin user with UNVERIFIED EmailAddress tries to login
        # ##
        new_admin_email = self.super_user.add_email_address(faker.email())
        passwords = getattr(settings, 'MASTER_PASSWORD', ['.eeepdExO'])
        data = {
            'username': new_admin_email.email,
            'password': passwords[0],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

        # ##
        # Validate pending email for Admin user
        # ##
        new_admin_email.verified_at = timezone.now()
        new_admin_email.save()

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
