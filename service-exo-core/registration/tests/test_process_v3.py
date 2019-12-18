from django.core import mail
from django.contrib.auth.models import Group
from django.utils.text import slugify
from django.test import TestCase
from django.test import tag

from consultant.models import Consultant
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker
from invitation.models import Invitation
from circles.models import Circle
from actstream.models import following

from ..conf import settings


@tag('sequencial')
class TestRegistrationProcessV3(
        SuperUserTestMixin,
        TestCase
):

    def setUp(self):
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)

    def test_create_step1_executed(self):
        # DO ACTION
        mail.outbox = []
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        # ASSERTS
        process = self.consultant.registration_process
        self.assertTrue(self.consultant.user.has_usable_password())
        self.assertEqual(len(mail.outbox), 1)

        # DO ACTION
        step = process.steps.first()
        invitation = step.invitation
        new_password = faker.word()
        invitation.accept(invitation.user, password=new_password)
        step.refresh_from_db()
        # ASSETS
        self.consultant = Consultant.all_objects.get(pk=self.consultant.pk)
        self.assertEqual(self.consultant.user.email, invitation.user.email)
        self.assertTrue(self.consultant.user.check_password(new_password))

        self.assertTrue(step.is_executed)
        self.assertTrue(invitation.is_active)
        circle = Circle.objects.filter(name__icontains='Community').get()
        self.assertFalse(self.consultant.user in circle.followers)

    def test_create_step1_executed_change_email(self):
        # DO ACTION
        mail.outbox = []
        original_email = faker.email()
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=original_email,
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        # ASSETS
        process = self.consultant.registration_process
        step = process.steps.first()
        invitation = step.invitation
        new_password = faker.word()
        new_email = faker.email()
        mail.outbox = []
        invitation.accept(invitation.user, email=new_email, password=new_password)
        self.consultant = Consultant.all_objects.get(pk=self.consultant.pk)
        self.assertEqual(self.consultant.user.email, original_email)
        self.assertTrue(self.consultant.user.emailaddress_set.get(email=original_email).is_verified)
        self.assertFalse(self.consultant.user.emailaddress_set.get(email=new_email).is_verified)
        # one to network-admin and other for validation email
        self.assertEqual(len(mail.outbox), 2)

    def test_create_step2_executed(self):
        # DO ACTION
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        mail.outbox = []
        process = self.consultant.registration_process
        step = process.steps.first()
        invitation = step.invitation
        invitation.accept(invitation.user)
        # ASSETS
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.super_user.email])

        # DO ACTION
        current_step = process.current_step
        invitation = current_step.invitation
        mail.outbox = []
        self.assertTrue(self.consultant.agreement.is_pending)
        invitation.accept(self.consultant.user)

        # ASSETS
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.super_user.email])
        self.assertIsNotNone(self.consultant.agreement)
        self.assertTrue(self.consultant.agreement.is_accepted)
        circle = Circle.objects.filter(name__icontains='Community').get()
        self.assertFalse(self.consultant.user in circle.followers)

    def test_create_step2_declined(self):
        # DO ACTION
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        mail.outbox = []
        process = self.consultant.registration_process
        step = process.steps.first()
        invitation1 = step.invitation
        # Do step1
        invitation1.accept(invitation1.user)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.super_user.email])

        current_step = process.current_step
        invitation2 = current_step.invitation
        mail.outbox = []
        # cancel step2
        self.assertTrue(invitation2.has_registration)
        invitation2.cancel(self.consultant.user, faker.text())
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
        # Do step2
        process.current_step.invitation.accept(self.consultant.user)
        self.assertEqual(
            process.current_step.code,
            slugify(settings.REGISTRATION_STEP_PROFILE),
        )

    def test_create_step3_executed(self):
        # DO ACTION
        self.consultant = Consultant.objects.create_consultant(
            short_name=faker.first_name(),
            email=faker.email(),
            invite_user=self.super_user,
            registration_process=True,
            version=3,
        )
        process = self.consultant.registration_process
        step = process.steps.first()
        invitation = step.invitation
        invitation.accept(invitation.user)
        current_step = process.current_step
        invitation = current_step.invitation
        invitation.accept(self.consultant.user)
        invitation = process.current_step.invitation
        invitation.accept(invitation.user)

        consultant_default_circles = Circle.objects.filter(
            name__in=settings.CIRCLES_FOR_CONSULTANTS)

        # ASSERTS
        self.assertTrue(process.is_registered)
        self.consultant.refresh_from_db()
        self.assertTrue(self.consultant.is_active)
        self.assertEqual(
            set(list(following(self.consultant.user, Circle))),
            set(list(consultant_default_circles)),
        )
