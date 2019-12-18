from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityMultiplePositionAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

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
        self.setup_credentials(self.super_user)

        TOTAL_APPLICANTS = 2
        applicants = []
        for _ in range(TOTAL_APPLICANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            applicant = models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
            applicants.append(applicant.pk)

        # DO ACTION
        for app_pk in applicants:
            url = reverse(
                'api:applicant-assign',
                kwargs={'pk': app_pk})

            data = {
                'response_message': faker.text(),
                'sow': self.get_sow_data(),
            }
            response = self.client.put(url, data=data)

            # ASSERTS
            app = models.Applicant.objects.get(pk=app_pk)
            self.assertTrue(status.is_success(response.status_code))
            self.assertTrue(app.is_selected)
            self.assertIsNotNone(app.sow)
            self.assertIsNotNone(app.sow.start_date)
            self.assertIsNotNone(app.sow.end_date)

        opp.refresh_from_db()
        self.assertTrue(opp.is_requested)

    @requests_mock.Mocker()
    def test_reject_applicant_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        self.setup_credentials(self.super_user)
        TOTAL_APPLICANTS = 2
        applicants = []
        for _ in range(TOTAL_APPLICANTS):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            applicant = models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
            applicants.append(applicant.pk)

        # DO ACTION
        for app_pk in applicants:
            url = reverse(
                'api:applicant-reject',
                kwargs={'pk': app_pk})
            data = {
                'response_message': faker.text()
            }
            response = self.client.put(url, data=data)

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
            opp.refresh_from_db()
            self.assertTrue(opp.is_requested)

    @requests_mock.Mocker()
    def test_initial_sow_applicant_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(duration_unity=settings.OPPORTUNITIES_DURATION_UNITY_WEEK)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())

        # DO ACTION
        self.setup_credentials(applicant.user)
        url = reverse(
            'api:applicant-init-sow',
            kwargs={'pk': applicant.pk})
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.data
        fields_from_opportunity = [
            'title', 'description', 'mode', 'location', 'place_id',
            'location_url', 'entity',
        ]
        for field in fields_from_opportunity:
            self.assertEqual(
                getattr(opp, field),
                data[field])
        self.assertEqual(data['start_date'], opp.start_date.isoformat())
        self.assertEqual(data['end_date'], opp.end_date.isoformat())

    @requests_mock.Mocker()
    def test_initial_sow_applicant_opportunity_for_hours(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(duration_unity=settings.OPPORTUNITIES_DURATION_UNITY_HOUR)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())

        # DO ACTION
        self.setup_credentials(applicant.user)
        url = reverse('api:applicant-init-sow', kwargs={'pk': applicant.pk})
        response = self.client.get(url)
        data = response.data

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data['start_date'], opp.start_date.isoformat())
        self.assertEqual(data['end_date'], opp.end_date.isoformat())

    @requests_mock.Mocker()
    def test_edit_sow_applicant_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        data = self.get_sow_data()
        opp.assign(self.super_user, applicant, **data)

        new_sow_data = {
            'sow': self.get_sow_data(),
            'response_message': faker.text(),
        }

        # DO ACTION
        self.setup_credentials(self.super_user)
        url = reverse('api:applicant-detail-sow', kwargs={'pk': applicant.pk})
        response = self.client.put(url, data=new_sow_data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        applicant.refresh_from_db()
        self.assertEqual(applicant.sow.title, new_sow_data['sow']['title'])

    @requests_mock.Mocker()
    def test_retrieve_sow_applicant_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        data = self.get_sow_data()
        opp.assign(self.super_user, applicant, **data)

        # DO ACTION
        users = [self.super_user, user]
        for user in users:
            self.setup_credentials(user)
            self.add_marketplace_permission(user)
            url = reverse(
                'api:applicant-detail-sow',
                kwargs={'pk': applicant.pk})
            response = self.client.get(
                url)

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
