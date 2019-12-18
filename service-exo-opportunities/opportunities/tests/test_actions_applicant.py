from datetime import timedelta

from django.utils import timezone
from django.test import TestCase

import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityApplicantActionTest(
        UserTestMixin,
        OpportunityTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_assign_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()

        TOTAL_APPLICANTS = 2
        applicants = []
        for _ in range(TOTAL_APPLICANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            applicant = models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
            applicants.append(applicant)

        # DO ACTION
        data = self.get_sow_data()
        for app in applicants:
            response_message = faker.text()
            opp.assign(self.super_user, app, response_message, **data)

            # ASSERTS
            self.assertTrue(app.is_selected)
            self.assertEqual(app.response_message, response_message)
            self.assertIsNotNone(app.sow)
        self.assertTrue(opp.is_requested)
        self.assertEqual(opp.applicants_info.count(), TOTAL_APPLICANTS)
        self.assertEqual(
            opp.applicants_info.filter_by_status_selected().count(),
            TOTAL_APPLICANTS)
        self.assertEqual(opp.selected_by, {self.super_user})

    @requests_mock.Mocker()
    def test_reject_applicant_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        TOTAL_APPLICANTS = 2
        applicants = []
        for _ in range(TOTAL_APPLICANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            applicant = models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
            applicants.append(applicant)

        # DO ACTION
        for app in applicants:
            response_message = faker.text()
            opp.reject(self.super_user, app, response_message)

            # ASSERTS
            self.assertTrue(opp.is_requested)
            self.assertEqual(opp.applicants_info.count(), TOTAL_APPLICANTS)

        self.assertEqual(
            opp.applicants_info.filter_by_status_rejected().count(),
            TOTAL_APPLICANTS)

    @requests_mock.Mocker()
    def test_assign_opportunity_after_rejected(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.reject(opp.created_by, applicant)
        response_message = faker.text()
        data = self.get_sow_data()

        # DO ACTION
        opp.assign(self.super_user, applicant, response_message, **data)

        # ASSERTS
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_selected)
        self.assertEqual(applicant.response_message, response_message)
        self.assertTrue(opp.is_requested)
        self.assertEqual(
            opp.applicants_info.filter_by_status_selected().count(),
            1)
        self.assertEqual(opp.selected_by, {self.super_user})
        self.assertIsNotNone(applicant.sow)

    @requests_mock.Mocker()
    def test_close_opportunity_when_positions_covered(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        opp.num_positions = 2
        opp.save()

        for _ in range(2):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            applicant = models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
            data = self.get_sow_data()

            # DO ACTION
            opp.assign(self.super_user, applicant, **data)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_closed)

    @requests_mock.Mocker()
    def test_open_closed_opportunity_after_rejecting(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        opp.num_positions = 1
        opp.deadline_date = (timezone.now() + timedelta(days=5)).date()
        opp.save()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        data = self.get_sow_data()
        opp.assign(self.super_user, applicant, **data)

        # DO ACTION
        opp.reject(opp.created_by, applicant)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_requested)
