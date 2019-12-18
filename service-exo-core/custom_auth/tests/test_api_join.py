from django.urls import reverse

from unittest.mock import patch

from rest_framework import status

from invitation.models import Invitation
from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from circles.models import Circle


class JoinUsTest(DjangoRestFrameworkTestCase):

    def generate_fake_data(self):
        return {
            'firstName': faker.first_name(),
            'lastName': faker.last_name(),
            'email': faker.email(),
            'password': faker.password(),
            'recaptcha': faker.word(),
            'entry_point': {
                'refereal': faker.name(),
                'website': 'canvas',
                'name': 'GET_CERTIFIED_FORM',
                'city': faker.name(),
            }
        }

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_join_us_ok(self, mock_email):
        # PREPARE DATA
        data = self.generate_fake_data()
        url = reverse('api:accounts:join-us')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(mock_email.called)
        data = response.json()
        invitation_hash = data['nextUrl'].split('/')[-1]
        invitation = Invitation.objects.get(hash=invitation_hash)
        user = invitation.user
        self.assertEqual(user.registration_process.steps.count(), 2)
        self.assertIsNotNone(user.registration_process.entry_point)
        circle = Circle.objects.filter(name__icontains='Community').get()
        self.assertFalse(user in circle.followers)

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_join_us_from_summits(self, mock_email):
        # PREPARE DATA
        data = self.generate_fake_data()
        data.pop('password')
        data.pop('lastName')
        data['customText'] = faker.text()
        url = reverse('api:accounts:join-us')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        data = response.json()
        invitation_hash = data['nextUrl'].split('/')[-1]
        invitation = Invitation.objects.get(hash=invitation_hash)
        user = invitation.user
        self.assertEqual(user.registration_process.steps.count(), 3)

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_join_us_previous_user(self, mock_email):
        # PREPARE DATA
        user = FakeUserFactory.create()
        data = self.generate_fake_data()
        data['email'] = user.email
        url = reverse('api:accounts:join-us')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(mock_email.called)
