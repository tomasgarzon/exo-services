from django.test import TestCase
from django.contrib.auth.models import Group
from django.test import tag

from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from registration.models import RegistrationProcess
from relation.faker_factories import FakeCustomerUserRoleFactory

from ..models import Invitation
from ..conf import settings


@tag('sequencial')
class InvitationTest(
    SuperUserTestMixin,
    TestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        group = Group.objects.get(name=settings.REGISTRATION_GROUP_NAME)
        group.user_set.add(self.super_user)

    def test_has_registration(self):
        # ##
        # Create a regular Invitation
        # ##
        role = FakeCustomerUserRoleFactory.create(user__is_active=True)
        user_to = role.user
        invitation = Invitation.objects.create_role_invitation(
            self.super_user,
            user_to,
            role,
        )

        self.assertIsNone(invitation.has_registration)

        # ##
        # Create a RegistrationProcess
        # ##
        consultant = FakeConsultantFactory.create()
        process = RegistrationProcess._create_process(
            self.super_user,
            consultant.user,
        )
        step = process.current_step
        self.assertIsNotNone(step.invitation.has_registration)

    def test_registration_step(self):
        # ##
        # Test for regular Invitation
        ###
        role = FakeCustomerUserRoleFactory.create(user__is_active=True)
        user_to = role.user
        invitation = Invitation.objects.create_role_invitation(
            self.super_user,
            user_to,
            role,
        )
        self.assertIsNone(invitation.registration_step)

        # ##
        # Test for Registration invitation
        # ##
        consultant = FakeConsultantFactory.create()
        process = RegistrationProcess._create_process(
            self.super_user,
            consultant.user,
        )
        step = process.current_step
        invitation = step.invitation

        self.assertEqual(
            invitation.registration_step,
            step,
        )
        self.assertEqual(
            invitation.registration_step.content_object,
            step.content_object,
        )
