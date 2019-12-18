from django.test import TestCase
from django.conf import settings
from django.test import tag

from mock import Mock

from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..models import Consultant
from ..middleware import ConsultantActivationMiddleware
from ..helpers.groups import group_waiting_list
from ..faker_factories import FakeConsultantFactory


@tag('sequencial')
class ConsultantRedirectOnBoardingTest(
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        self.create_superuser()
        self.request = Mock()
        self.request.META = {}
        self.request.session = {}

    def test_do_logout_step3(self):
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
        invitation = step.invitation
        invitation.accept(invitation.user)
        current_step = process.current_step
        invitation = current_step.invitation
        invitation.accept(self.consultant.user)
        mock = Mock()
        self.middleware = ConsultantActivationMiddleware(mock)
        # DO ACTION
        self.request.path = '/accounts/logout/'
        self.request.user = self.consultant.user
        response = self.middleware(self.request)

        # ASSERTS
        self.assertIsNotNone(response)
        self.assertTrue(isinstance(response, Mock))

    def test_waiting_list_redirect(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            user__is_active=True,
            user__password='123456',
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        consultant.user.groups.add(group_waiting_list())

        # DO ACTION
        mock = Mock()
        self.middleware = ConsultantActivationMiddleware(mock)
        # DO ACTION
        self.request.path = consultant.get_public_profile_v2()
        self.request.user = consultant.user
        response = self.middleware(self.request)

        # ASSERTS
        self.assertIsNotNone(response)
        self.assertTrue(isinstance(response, Mock))
