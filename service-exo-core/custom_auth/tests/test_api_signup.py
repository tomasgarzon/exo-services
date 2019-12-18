from django.core import mail
from django.contrib.auth.models import Group
from django.conf import settings
from django.urls import reverse
from django.test import tag

from rest_framework import status

from consultant.models import Consultant
from test_utils.test_case_mixins import SuperUserTestMixin
from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker


@tag('sequencial')
class TestSignupRegistrationProcessV3(
        SuperUserTestMixin, DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)

    def test_accept_step1(self):
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        mail.outbox = []
        process = self.consultant.registration_process
        step = process.current_step
        invitation = step.invitation
        url = reverse('api:accounts:signup', kwargs={'hash': invitation.hash})
        user_password = faker.word()
        data = {
            'email': faker.email(),
            'password': user_password,
        }
        response = self.client.post(url, data=data, format='json')

        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(response.data['nextUrl'])
        self.assertIsNotNone(response.data['token'])
        self.assertIn('_auth_user_id', self.client.session)
        self.consultant.user.refresh_from_db()

        self.assertTrue(self.consultant.user.check_password(user_password))
        self.assertTrue(self.consultant.user.email, data['email'])

        invitation.refresh_from_db()
        self.assertTrue(invitation.is_active)
        self.assertEqual(len(mail.outbox), 2)
        process.refresh_from_db()
        invitation = process.current_step.invitation
        self.assertEqual(
            response.data['nextUrl'],
            invitation.validation_object.get_public_url(invitation),
        )

    def test_bad_request_step1(self):
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        mail.outbox = []
        process = self.consultant.registration_process
        step = process.current_step
        invitation = step.invitation
        url = reverse('api:accounts:signup', kwargs={'hash': invitation.hash})
        data = {
            'email': '',
            'password': '',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))

    def test_email_invalid_step1(self):
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        mail.outbox = []
        process = self.consultant.registration_process
        step = process.current_step
        invitation = step.invitation
        url = reverse('api:accounts:signup', kwargs={'hash': invitation.hash})
        data = {
            'email': self.super_user.email,
            'password': faker.word(),
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
