from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from mock import patch

from exo_accounts.models import EmailAddress
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from utils.faker_factory import faker


class TestAPIEmailAddress(
    UserTestMixin,
    SuperUserTestMixin,
    DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()

    @patch.object(EmailAddress, 'send_verification')
    def test_change_email(self, mock_send_verification):

        user_email = faker.email()
        user_pwd = faker.text()
        user = get_user_model().objects.create_user(
            email=user_email,
            password=user_pwd,
            short_name=faker.first_name(),
        )

        url = reverse('api:accounts:validate-email')

        # Logged user
        self.client.login(username=self.super_user.email, password='123456')
        data = {
            'user': user.pk,
            'email': user_email,
        }

        # admin user
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))

        # own user
        self.client.login(username=user.email, password=user_pwd)
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))

        # ##
        # not valid email
        # ##

        other_email = faker.email()
        get_user_model().objects.create_user(
            email=other_email,
            password=user_pwd,
            short_name=faker.first_name(),
        )
        data['email'] = other_email
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

    @patch.object(EmailAddress, 'send_verification')
    def test_discard_email(self, mock):

        user = FakeUserFactory()
        new_email = faker.email()
        email = EmailAddress.objects.create(
            user=user,
            email=new_email,
        )

        url = reverse('api:accounts:discard-email')
        data = {
            'verif_key': email.verif_key,
            'email': email.pk,
        }

        # ##
        # User not logged
        # ##

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        # ##
        # Logged user
        # ##

        self.client.login(username=user.email, password=user.short_name)

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))

        # ##
        # Check an Email already verified
        # ##

        new_email_1 = faker.email()
        new_email_1_address = user.add_email_address(new_email_1, True)

        data = {
            'verif_key': new_email_1_address.verif_key,
            'email': new_email_1_address.pk,
        }

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
        # ##
        # Use an invalid key
        # ##

        data_fail = {
            'verif_key': faker.name(),
            'email': new_email_1_address.pk,
        }
        response = self.client.post(url, data=data_fail, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

    @patch.object(EmailAddress, 'send_verification')
    def test_resend_verification_email(self, mock):

        user = FakeUserFactory()
        new_email = faker.email()
        EmailAddress.objects.create(user=user, email=new_email)

        # ##
        # Not logged user
        # ##

        url = reverse('api:accounts:resend-email')
        data = {
            'user': user.pk,
            'email': new_email,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

        # ##
        # Check not valid email
        # ##

        data = {
            'user': user.pk,
            'email': faker.name(),
        }
        self.client.login(username=user.email, password=user.short_name)

        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEqual(
            response.data.get('email'),
            ['Enter a valid email address.'],
        )

        # ##
        # Logged user with correct data
        # ##

        data = {
            'user': user.pk,
            'email': new_email,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data.get('status'))

        # ##
        # Already verified email
        # ##

        new_email_1 = faker.email()
        user.add_email_address(new_email_1, True)

        data = {
            'user': user.pk,
            'email': new_email_1,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

        # ##
        # Email does not exist
        # ##

        data = {
            'user': user.pk,
            'email': faker.email(),
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
