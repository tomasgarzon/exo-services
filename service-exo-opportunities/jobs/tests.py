from django.test import TestCase

import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from opportunities import models
from opportunities.tests.test_mixin import OpportunityTestMixin, request_mock_account

from .models import Job


class JobApplicantTest(
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
    def test_create_job(self, mock_request):
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
            self.assertIsNotNone(app.sow)
            self.assertIsNotNone(app.job)

    @requests_mock.Mocker()
    def test_reject_after_assign_opportunity(self, mock_request):
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
        opp.assign(self.super_user, applicant, response_message, **data)
        self.assertTrue(Job.objects.filter(applicant=applicant).exists())

        # DO ACTION
        response_message = faker.text()
        opp.reject(self.super_user, applicant, response_message)

        # ASSERTS
        self.assertFalse(Job.objects.filter(applicant=applicant).exists())
