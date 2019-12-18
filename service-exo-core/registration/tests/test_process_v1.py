from django.core import mail
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.test import tag, TestCase

from consultant.faker_factories import (
    FakeConsultantFactory
)

from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker
from invitation.models.invitation import Invitation
from ..models import RegistrationProcess, RegistrationProcessTemplate
from ..conf import settings


@tag('sequencial')
class TestRegistrationProcess(
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)
        self.template = RegistrationProcessTemplate.objects.filter(version=2).last()
        self.consultant = FakeConsultantFactory.create()

    def test_create_process(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
        )

        # ASSERTS
        self.assertIsNotNone(process.id)
        self.assertEqual(
            process.steps.count(),
            process.template.steps.count(),
        )
        step = process.steps.first()
        self.assertTrue(step.is_current)
        consultant_validation = step.content_object
        self.assertIsNotNone(consultant_validation)

        for step in process.steps.exclude(pk=step.pk):
            self.assertTrue(step.is_pending)

    def test_invitation_property(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
        )

        # ASSERTS
        step = process.steps.first()
        self.assertIsNotNone(step.invitation)
        self.assertEqual(
            step.invitation,
            Invitation.objects.get(
                invite_user=self.super_user,
                user=self.consultant.user,
            ),
        )

    def test_auto_start_process(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            auto_start=False,
        )

        # ASSERTS
        self.assertIsNotNone(process)
        self.assertIsNone(process.current_step)
        for step in process.steps.all():
            self.assertTrue(step.is_pending)
            self.assertIsNone(step.content_object)
            self.assertIsNone(step.invitation)

    def test_current_step_status(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
        )

        # ASSERTS
        self.assertEqual(
            process.current_step.status,
            settings.REGISTRATION_CH_CURRENT,
        )

    def test_current_step_for_fist_step(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
        )

        # ASSERTS
        self.assertEqual(
            process.current_step,
            process.steps.first(),
        )

    def test_current_step_for_second_step(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            process_template=self.template,
        )

        #  ASSERTS
        step = process.steps.first()
        invitation = step.invitation
        invitation.accept(self.super_user)

        self.assertEqual(
            process.current_step.code,
            process.steps.all()[1].code,
        )

    def test_create_step1(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            process_template=self.template,
        )
        # ASSETS
        self.assertTrue(self.consultant.agreements.count() == 1)
        step = process.steps.first()
        validation = step.content_object
        invitation = step.invitation
        self.assertIsNotNone(validation)
        self.assertTrue(invitation.is_pending)

    def test_create_step1_executed(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            process_template=self.template,
        )
        # ASSERTS
        self.assertTrue(self.consultant.agreements.count() == 1)
        step = process.steps.first()
        mail.outbox = []
        process.execute_step(self.consultant.user, step.code)
        self.assertTrue(process.steps.first().is_executed)

        # Exist an option to avoid send user email
        if process.check_option(settings.REGISTRATION_OPTION_SEND_USER_EMAIL):
            self.assertEqual(len(mail.outbox), 2)
        else:
            self.assertEqual(len(mail.outbox), 1)

    def test_filter_queryset_by_content_object(self):
        # DO ACTION
        consultant = FakeConsultantFactory.create()
        RegistrationProcess._create_process(
            self.super_user,
            consultant.user,
            process_template=self.template,
        )
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
        )
        step = process.steps.first()
        validation = step.content_object
        object_id = validation.id
        content_type_id = ContentType.objects.get_for_model(validation).id
        p1 = RegistrationProcess.objects.filter_by_content_object_pending(
            object_id,
            content_type_id,
        )
        self.assertEqual(p1.count(), 1)
        process.execute_step(self.consultant.user, step.code)
        p1 = RegistrationProcess.objects.filter_by_content_object_pending(
            object_id,
            content_type_id,
        )
        self.assertEqual(p1.count(), 0)

    def test_activate_invitation(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            process_template=self.template,
        )
        # ASSERTS
        step = process.steps.first()
        invitation = step.invitation
        invitation.accept(self.super_user)

        step.refresh_from_db()
        self.assertTrue(step.is_executed)
        self.assertIsNotNone(self.consultant.agreement)
        self.assertTrue(self.consultant.agreement.is_accepted)

    def test_decline_invitation(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            process_template=self.template,
        )
        # ASSERTS
        step = process.steps.first()
        invitation = step.invitation
        error_message = faker.text()
        invitation.accept(self.consultant.user)

        invitation = process.current_step.invitation
        invitation.cancel(
            self.super_user,
            description=error_message,
        )

        invitation.refresh_from_db()
        step.refresh_from_db()
        self.assertTrue(step.is_current)
        self.assertEqual(self.consultant.validations.waiting().count(), 1)
        self.assertEqual(invitation.description_response, error_message)

    def test_cancel_step(self):
        # DO ACTION
        consultant = FakeConsultantFactory.create()
        process = RegistrationProcess._create_process(
            self.super_user,
            consultant.user,
            process_template=self.template,
        )

        # ASSERTS
        invitation = process.current_step.invitation
        self.assertTrue(invitation.can_be_accepted(consultant.user))
        self.assertTrue(invitation.can_be_accepted(self.super_user))

        invitation.cancel(consultant.user)

        self.assertIsNotNone(process.current_step)
        self.assertEqual(process.steps.first().code, process.current_step.code)
        current_step = process.steps.first()
        invitation = current_step.invitation

        self.assertTrue(current_step.is_current)
        self.assertTrue(current_step.invitation.is_pending)
        self.assertTrue(invitation.can_be_accepted(consultant.user))
        self.assertTrue(invitation.can_be_accepted(self.super_user))

    def test_current_step(self):
        # DO ACTION
        consultant1 = FakeConsultantFactory.create()
        process1 = RegistrationProcess._create_process(
            self.super_user,
            consultant1.user,
            process_template=self.template,
        )
        # ASSERTS
        step = process1.steps.first()
        # Check for step 1
        self.assertEqual(
            process1.current_step.code,
            step.code,
        )
        step.invitation.accept(self.super_user)

        step = process1.steps.all()[1]
        # Check for step 2
        self.assertEqual(
            process1.current_step.code,
            step.code,
        )
        # ##
        # Check current step for cancelled step
        # ##
        consultant2 = FakeConsultantFactory.create()
        process2 = RegistrationProcess._create_process(
            self.super_user,
            consultant2.user,
            process_template=self.template,
        )

        step = process2.steps.first()
        # Check for step 1
        self.assertEqual(
            process2.current_step.code,
            step.code,
        )
        step.invitation.cancel(self.super_user)
        step.refresh_from_db()
        self.assertIsNotNone(process2.current_step)

    def test_get_next_step_public_url(self):
        # DO ACTION
        consultant = FakeConsultantFactory.create()
        process = RegistrationProcess._create_process(
            self.super_user,
            consultant.user,
            process_template=self.template,
        )
        # ASSERTS
        first_step_url = process.get_next_step_public_url()
        self.assertEqual(
            process.get_next_step_public_url(),
            process.steps.first().public_url,
        )

        invitation = process.current_step.invitation
        invitation.accept(consultant.user)

        self.assertNotEqual(
            first_step_url,
            process.get_next_step_public_url(),
        )
        self.assertEqual(
            process.get_next_step_public_url(),
            process.steps.all()[1].public_url,
        )

    def test_reactivate_step(self):
        # DO ACTION
        consultant = FakeConsultantFactory.create()
        process = RegistrationProcess._create_process(
            self.super_user,
            consultant.user,
            process_template=self.template,
        )
        # ASSERTS
        invitation = process.current_step.invitation
        invitation.cancel(self.super_user)

        # If we resend the invitation the process is Re-Activated
        invitation.resend(self.super_user)

        current_step = process.current_step
        invitation = current_step.invitation

        self.assertTrue(invitation.is_pending)
        self.assertTrue(invitation.can_be_accepted(consultant.user))
        self.assertTrue(invitation.can_be_accepted(self.super_user))

    def test_create_process_with_no_skill(self):
        # DO ACTION
        process = RegistrationProcess._create_process(
            self.super_user,
            self.consultant.user,
            skip_steps=['skill-assessment'],
            process_template=self.template,
        )
        self.assertIsNotNone(process.id)
        self.assertNotEqual(
            process.steps.count(), process.template.steps.count(),
        )
        self.assertEqual(process.steps.count(), 2)
        step = process.steps.first()
        self.assertEqual(step.next_steps.first().code, 'sign-up')
