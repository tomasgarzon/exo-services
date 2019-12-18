from django.test import tag, TestCase
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.conf import settings

from mock import patch
from rest_framework import status

from test_utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker

from ..models import Consultant
from ..conf import ConsultantConfig
from ..search import consultant_settings


@tag('sequencial')
class TestConsultantNetworkList(
    UserTestMixin,
    TestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()
        perm = Permission.objects.get(
            codename=settings.CONSULTANT_PERMS_CONSULTANT_LIST_AND_EXPORT)
        self.user.user_permissions.add(perm)
        self.consultants_registration = []
        for _ in range(3):
            self.consultants_registration.append(
                Consultant.objects.create_consultant(
                    short_name=faker.name(),
                    full_name=faker.name(),
                    email=faker.email(),
                    invite_user=self.user,
                    registration_process=True,
                    skip_steps=[],
                    custom_text=faker.text(),
                )
            )

    def test_search_consultant_registration_status_signup(self):
        # DO ACTION
        queryset = Consultant.all_objects.all()
        results = queryset.filter(status=ConsultantConfig.STATUS_CH_PENDING_VALIDATION)

        # ASSERTS
        self.assertEqual(results.count(), 3)

    def test_search_consultant_registration_status_agreement(self):
        # PREPARE DATA
        consultant_1 = self.consultants_registration[0]
        consultant_2 = self.consultants_registration[1]

        # DO ACTION
        consultant_1_sign_up = consultant_1.user.invitations.last()
        consultant_1_sign_up.accept(consultant_1.user)
        consultant_2_sign_up = consultant_2.user.invitations.last()
        consultant_2_sign_up.accept(consultant_2.user)

        # ASSERTS
        self.assertEqual(
            consultant_1.registration_process.current_step.code,
            consultant_settings.SLUG_REGISTRATION_STEP_AGREEMENT
        )
        self.assertEqual(
            consultant_2.registration_process.current_step.code,
            consultant_settings.SLUG_REGISTRATION_STEP_AGREEMENT
        )

    @patch('consultant.tasks.NetworkListReportTask.apply_async')
    def test_xlsx_report(self, mock_task):
        # PREPARE DATA
        url = reverse('consultant:export-csv')
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_redirect(response.status_code))
        self.assertTrue(mock_task.called)
