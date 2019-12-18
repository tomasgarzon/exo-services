from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.test import tag

from rest_framework import status
from rest_framework.test import APIClient

from frontend.helpers import UserRedirectController
from test_utils.test_case_mixins import SuperUserTestMixin
from test_utils.test_views_mixin import TestViewMixin
from utils.faker_factory import faker

from ..models import Consultant, ConsultantValidation
from .test_consultant_mixin import TestConsultantMixin


@tag('sequencial')
class ConsultantTest(
        SuperUserTestMixin,
        TestConsultantMixin,
        TestViewMixin,
        TestCase):
    """
    Test for Consultant Creation method and basic status checks
    """

    def setUp(self):
        self.create_superuser()

    def test_consultant_without_validations(self):
        consultant = Consultant.objects.create_consultant(
            short_name=faker.name(),
            email=faker.email(),
            validations=[],
            invite_user=self.super_user,
        )

        self.assertIsNotNone(consultant)
        self.assertEqual(consultant.languages.count(), 1)  # english by default
        self.assertEqual(
            consultant.status,
            settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION,
        )

    def test_consultant_create(self):
        """
        Test to create a Consultant user with a Validation that
        will not be accepted
        """
        consultant = Consultant.objects.create_consultant(
            short_name=faker.name(),
            email=faker.email(),
            languages=['Spanish', 'English'],
            validations=ConsultantValidation.objects.all().values_list(
                'name',
                flat=True,
            ),
            invite_user=self.super_user,
        )

        self.assertIsNotNone(consultant)
        self.assertEqual(
            consultant.status,
            settings.CONSULTANT_STATUS_CH_PENDING_VALIDATION,
        )

    def test_consultant_create_frontend(self):
        # PREPARE DATA
        name = faker.name()
        email = faker.email()
        custom_text = faker.text()
        self.login(username=self.super_user.username, password='123456')

        url = reverse('consultant:add')
        data = {
            'name': name,
            'email': email,
            'custom_text': custom_text,
        }

        # DO ACTION
        response = self.post(url, data)

        # ASSERTS
        consultant = Consultant.all_objects.get(user__email=email)
        self.assertIsNotNone(consultant)
        self.assertEqual(consultant.user.short_name, name.split(' ')[0])
        self.assertEqual(consultant.user.full_name, name)
        self.assertTrue(status.is_redirect(response.status_code))
        self.assertEqual(response.url, reverse('consultant:list'))

    def validate_consultant_process(self, consultant):
        process = consultant.registration_process
        step = process.steps.first()
        invitation = step.invitation
        invitation.accept(invitation.user)
        current_step = process.current_step
        invitation = current_step.invitation
        invitation.accept(consultant.user)
        invitation = process.current_step.invitation
        invitation.accept(invitation.user)

    def test_consultant_create_waiting_list(self):
        # PREPARE DATA
        name = faker.name()
        email = faker.email()
        custom_text = faker.text()
        self.login(username=self.super_user.username, password='123456')

        url = reverse('consultant:add')
        data = {
            'name': name,
            'email': email,
            'custom_text': custom_text,
            'waiting_list': True
        }

        # DO ACTION
        response = self.post(url, data)
        consultant = Consultant.all_objects.get(user__email=email)
        self.validate_consultant_process(consultant)
        self.enable_advising_for_consultant(consultant)

        # ASSERTS
        self.assertIsNotNone(consultant)
        self.assertTrue(status.is_redirect(response.status_code))
        self.assertEqual(response.url, reverse('consultant:list'))
        self.assertTrue(consultant.is_in_waiting_list)
        url, zone = UserRedirectController.redirect_url(consultant.user)
        self.assertEqual(
            url,
            consultant.get_public_profile_v2()
        )
        self.assertFalse(zone)

    def test_consultant_api_create(self):
        # PREPARE DATA
        name = faker.name()
        email = faker.email()
        custom_text = faker.text()
        client = APIClient()
        client.login(username=self.super_user.username, password='123456')

        url = reverse('api:consultant:create')
        data = {
            'name': name,
            'email': email,
            'custom_text': custom_text,
            'waiting_list': True,
            'coins': 20,
        }

        # DO ACTION
        response = client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Consultant.all_objects.filter(user__email=data['email']).count(), 1)
        consultant = Consultant.all_objects.filter(user__email=data['email']).get()
        self.assertEqual(response.data['user_id'], consultant.user.pk)
        self.assertEqual(response.data['id'], consultant.pk)
        self.assertIsNotNone(response.data['registration_url'])

    def test_consultant_api_create_with_duplicated_email(self):
        # PREPARE DATA
        name = faker.name()
        email = faker.email()
        custom_text = faker.text()
        client = APIClient()
        client.login(username=self.super_user.username, password='123456')

        url = reverse('api:consultant:create')
        data = {
            'name': name,
            'email': email,
            'custom_text': custom_text,
            'waiting_list': True,
            'coins': 20,
        }

        # DO ACTION
        response = client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        # DO ACTION
        data['email'] = data['email'].upper()
        response = self.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_consultant_add_with_duplicated_email(self):
        # PREPARE DATA
        name = faker.name()
        email = faker.email()
        custom_text = faker.text()
        self.login(username=self.super_user.username, password='123456')

        url = reverse('consultant:add')
        data = {
            'name': name,
            'email': email,
            'custom_text': custom_text,
        }

        # DO ACTION
        response = self.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_redirect(response.status_code))

        # DO ACTION
        data['email'] = data['email'].upper()
        response = self.post(url, data)

        # ASSERTS
        self.assertFalse(response.context_data.get('form').is_valid())
