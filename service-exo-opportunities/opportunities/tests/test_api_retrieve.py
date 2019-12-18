from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account
from ..faker_factories import FakeOpportunityFactory


class OpportunityRetrieveAPITest(
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
    def test_consultant_retrieve_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.get(url)
        data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNone(
            data['myApplicant'])
        self.assertEqual(
            data['userStatus'],
            settings.OPPORTUNITIES_CH_APPLICANT_DRAFT)
        self.assertEqual(
            len(data['applicants']), 0)
        self.assertIsNotNone(
            data['requestedBy'])
        self.assertEqual(len(data['budgets']), 2)

    @requests_mock.Mocker()
    def test_owner_admin_retrieve_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        for _ in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
        self.setup_credentials(self.super_user)
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.get(url)
        data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNone(data['myApplicant'])
        self.assertEqual(len(data['applicants']), 3)
        self.assertIsNotNone(data['requestedBy'])

    @requests_mock.Mocker()
    def test_owner_admin_retrieve_opportunity_tagged(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        owner_user = self.get_user()
        self.add_marketplace_permission(owner_user)
        request_mock_account.add_mock(
            owner_user, is_consultant=True, is_superuser=False)
        users = []
        for _ in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            users.append(user)
        opp = FakeOpportunityFactory.create(
            user_from=owner_user,
            target=settings.OPPORTUNITIES_CH_TARGET_FIXED,
            users_tagged=users)

        self.setup_credentials(owner_user)
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.get(url)
        data = response.json()
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(data['usersTagged']), 3)
        self.assertIsNotNone(data['requestedBy'])

    @requests_mock.Mocker()
    def test_applicant_order_in_opportunity_detail(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        url = reverse('api:opportunity-admin', kwargs={'pk': opp.pk})

        order_expected = []

        # SELECTED
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        order_expected.append(app)
        opp.assign(self.super_user, app, faker.text(), **self.get_sow_data())

        # REQUESTED
        for k in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            app = models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
            order_expected.insert(1, app)

        # REJECTED
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        order_expected.append(app)
        opp.reject(opp.created_by, app, faker.text())

        # DO ACTION
        self.setup_credentials(self.super_user)
        response = self.client.get(url, data={})
        self.assertTrue(status.is_success(response.status_code))
        applicants = response.data.get('applicants')

        for index, app in enumerate(order_expected):
            self.assertEqual(applicants[index]['id'], app.pk)

    @requests_mock.Mocker()
    def test_retrieve_opportunity_removed(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        opp.remove(opp.created_by)
        other_user = self.get_user()
        self.add_marketplace_permission(other_user)
        request_mock_account.add_mock(
            other_user, is_consultant=True, is_superuser=False)
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})

        # DO ACTION
        for user in [self.super_user, other_user]:
            self.setup_credentials(user)
            response = self.client.get(url)
            # ASSERTS
            self.assertEqual(
                response.status_code,
                status.HTTP_410_GONE)

    @requests_mock.Mocker()
    def test_retrieve_opportunity_closed(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        opp.close(self.super_user, faker.text())
        other_user = self.get_user()
        self.add_marketplace_permission(other_user)
        request_mock_account.add_mock(
            other_user, is_consultant=True, is_superuser=False)
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})

        # DO ACTION
        self.setup_credentials(other_user)
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(
            status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(
            data['status'],
            settings.OPPORTUNITIES_CH_CLOSED)
        self.assertEqual(
            data['userActions'],
            [])
