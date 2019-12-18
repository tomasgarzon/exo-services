from django.core import mail
from django.utils.text import slugify
from django.test import tag

from django.test import TestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from registration.models import RegistrationProcess
from invitation.models import Invitation

from ..faker_factories import FakeConsultantFactory
from ..tests.test_consultant_mixin import TestConsultantMixin
from ..conf import settings


@tag('sequencial')
class ConsultantDisableTest(
        TestConsultantMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create()

    def test_disable_consultant_without_process(self):
        self.consultant.disable(self.super_user)
        self.assertTrue(self.consultant.is_disabled)

    def test_disable_active_consultant_process_not_started(self):
        RegistrationProcess._create_process(self.super_user, self.consultant.user)
        # Disable consultant
        self.consultant.disable(self.super_user)
        self.assertTrue(self.consultant.is_disabled)
        self.assertEqual(
            self.consultant.status_detail,
            self.consultant.get_status_display(),
        )
        # Re-activate consultant
        mail.outbox = []
        self.consultant.reactivate(self.super_user)
        self.assertTrue(self.consultant.is_pending_validation)
        self.assertEqual(self.consultant.get_pending_validations().count(), 1)
        validation = self.consultant.get_pending_validations()[0]
        self.assertTrue(validation.is_sent)
        invitation = Invitation.objects.filter_by_object(validation)[0]
        self.assertTrue(invitation.is_pending)
        self.assertEqual(len(mail.outbox), 1)

    def test_disable_active_consultant_certified(self):
        process = RegistrationProcess._create_process(
            self.super_user, self.consultant.user)
        step = process.steps.first()
        invitation = step.invitation
        invitation.accept(self.super_user)
        step = process.steps.all()[1]
        step.invitation.accept(self.consultant.user)
        step = process.steps.all()[2]
        step.invitation.accept(self.consultant.user)
        self.assertTrue(process.is_registered)
        self.consultant.disable(self.super_user)
        self.assertTrue(self.consultant.is_disabled)
        self.assertEqual(self.consultant.get_pending_validations().count(), 0)
        self.consultant.reactivate(self.super_user)
        self.assertTrue(self.consultant.is_active)
        self.assertEqual(
            self.consultant.status_detail,
            self.consultant.get_status_display(),
        )

    def test_disable_active_consultant_no_registration_no_skill(self):
        self.consultant.disable(self.super_user)
        self.assertTrue(self.consultant.is_disabled)
        mail.outbox = []
        self.consultant.reactivate(self.super_user)
        self.assertTrue(self.consultant.is_pending_validation)
        self.assertIsNotNone(self.consultant.registration_process)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            self.consultant.status_detail,
            slugify(settings.REGISTRATION_STEP_SIGNUP),
        )
