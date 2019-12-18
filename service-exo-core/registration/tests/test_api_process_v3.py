from django.core import mail
from django.contrib.auth.models import Group
from django.utils.text import slugify
from django.test import tag
from django.urls import reverse
from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from consultant.models import Consultant
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker
from invitation.models import Invitation

from ..conf import settings


STEPS_NAMES = settings.REGISTRATION_STEPS_NAMES


@tag('sequencial')
class TestAPIRegistrationProcessV3(
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)

    def test_create_step2_declined(self):
        # PREPARE DATA

        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        process = self.consultant.registration_process
        step = process.steps.first()
        invitation1 = step.invitation
        # Do step1
        invitation1.accept(invitation1.user, password='123456')
        current_step = process.current_step
        invitation2 = current_step.invitation
        url = reverse(
            'api:invitation:invitation-decline',
            kwargs={'hash': invitation2.hash})
        self.client.login(username=self.consultant.user.email, password='123456')
        mail.outbox = []

        # DO ACTION
        response = self.client.post(url, data={'declined_message': faker.text()})
        invitation2.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(invitation2.has_registration)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.super_user.email])
        self.assertEqual(process.current_step.code, step.code)
        self.assertTrue(process.current_step.invitation.is_pending)
        self.assertTrue(
            Invitation.objects.filter(pk=invitation2.pk).exists(),
        )
        self.assertEqual(
            process.current_step.code,
            slugify(settings.REGISTRATION_STEP_SIGNUP),
        )
        # do step1 again
        process.current_step.invitation.accept(self.consultant.user, password=faker.word())
        self.assertEqual(
            process.current_step.code,
            slugify(settings.REGISTRATION_STEP_AGREEMENT),
        )

    def test_create_step_agreement_declined(self):
        # PREPARE DATA

        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            full_name=faker.name(),
            email=faker.email(),
            password='123456',
            registration_process=True,
            skip_steps=[STEPS_NAMES[2][0]],
            version=3,
        )
        process = self.consultant.registration_process
        step = process.steps.first()
        # Decline step1
        invitation = step.invitation
        url = reverse(
            'api:invitation:invitation-decline',
            kwargs={'hash': invitation.hash})
        self.client.login(username=self.consultant.user.email, password='123456')

        # DO ACTION
        response = self.client.post(url, data={'declined_message': faker.text()})
        invitation.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(self.consultant.registration_process_current_url)

        self.assertEqual(
            process.current_step.code,
            slugify(settings.REGISTRATION_STEP_AGREEMENT),
        )
        # do step1 again
        process.current_step.invitation.accept(self.consultant.user)
        self.assertEqual(
            process.current_step.code,
            slugify(settings.REGISTRATION_STEP_PROFILE),
        )
