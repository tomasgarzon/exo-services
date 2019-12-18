from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from auth_uuid.utils.user_wrapper import UserWrapper

from utils.test_mixin import UserTestMixin

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityListAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_super_user()

        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def create_initial_scenario(self):
        # CREATE 3 REQUESTED
        for _ in range(3):
            opp = self.create_opportunity()

        # Create an applicant for last opportunity requested

        user = self.get_user()

        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")

        # CREATE 1 ASSIGNED
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app)

        # CREATE 2 CLOSED
        for _ in range(2):
            opp = self.create_opportunity()
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            app = opp.create_open_applicant(
                user, user, summary="")
            opp.assign(self.super_user, app)
            opp.close(self.super_user)

        # CREATE 2 REMOVED
        for _ in range(2):
            opp = self.create_opportunity()
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            app = opp.create_open_applicant(
                user, user, summary="")
            opp.assign(self.super_user, app)
            opp.remove(
                self.super_user,
                comment='',
            )
        return [3, 1, 2]

    @requests_mock.Mocker()
    def test_simple(self, m):
        self.init_mock(m)
        request_mock_account.add_mock(
            self.super_user,
            is_consultant=False,
            is_superuser=True)
        user_wrapper = UserWrapper(user=self.super_user)
        self.assertTrue(user_wrapper.is_superuser)

    def retrieve_opportunity(self, pk):
        url = reverse('api:opportunity-detail', kwargs={'pk': pk})
        response = self.client.get(url, data={})
        self.assertTrue(status.is_success(response.status_code))

    def retrieve_admin_opportunity(self, pk):
        url = reverse('api:opportunity-admin', kwargs={'pk': pk})
        response = self.client.get(url, data={})
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_opportunities_superuser_all(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        [requested, assigned, _] = self.create_initial_scenario()
        url = reverse('api:opportunity-list')
        # DO ACTION
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], requested + assigned)

        for opp in response.json()['results']:
            self.assertIsNotNone(opp['numApplicants'])
            self.retrieve_admin_opportunity(opp['pk'])

    @requests_mock.Mocker()
    def test_opportunities_superuser_published_by_you(self, mock_request):
        # PREPARE DATA
        num_user_opportunities = 6
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        url = reverse('api:opportunity-list')
        all_opp = self.create_initial_scenario()

        for _ in range(num_user_opportunities):
            self.create_opportunity(user=self.super_user)

        # DO ACTION
        response = self.client.get(url, data={'published_by_you': True})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], sum(all_opp) + num_user_opportunities)
        for opp in response.json()['results']:
            self.retrieve_admin_opportunity(opp['pk'])

    @requests_mock.Mocker()
    def test_opportunities_not_superuser_published_by_you(self, mock_request):
        # PREPARE DATA
        num_user_opportunities = 6
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        self.create_initial_scenario()

        for _ in range(num_user_opportunities):
            self.create_opportunity(user=user)
        opp = self.create_opportunity(user=user)
        opp.remove(user)
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.get(url, data={'published_by_you': True})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], num_user_opportunities)
        for opp in response.json()['results']:
            self.retrieve_admin_opportunity(opp['pk'])

    @requests_mock.Mocker()
    def test_opportunities_consultant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        [requested, assigned, _] = self.create_initial_scenario()
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], requested + assigned)
        for opp in response.json()['results']:
            self.retrieve_opportunity(opp['pk'])
            opportunity = models.Opportunity.objects.get(pk=opp['pk'])
            self.assertTrue(opportunity.has_seen(user))

    @requests_mock.Mocker()
    def test_opportunities_assigned_consultant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        [requested, assigned, _] = self.create_initial_scenario()
        opp = models.Opportunity.objects.filter_by_applicants_assigned().filter_by__status_requested().first()
        user = opp.applicants.first()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], requested + assigned)
        for opp in response.json()['results']:
            self.retrieve_opportunity(opp['pk'])

    @requests_mock.Mocker()
    def test_opportunities_closed_consultant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        [requested, assigned, _] = self.create_initial_scenario()
        opp = models.Opportunity.objects.filter_by__status_closed().first()
        user = opp.applicants.first()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], requested + assigned + 1)
        self.assertTrue(
            opp.pk in [o['pk'] for o in response.json()['results']])
        for opp in response.json()['results']:
            self.retrieve_opportunity(opp['pk'])

    @requests_mock.Mocker()
    def test_opportunities_visited(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.create_initial_scenario()
        opp = models.Opportunity.objects.all().first()

        user = opp.applicants.first()

        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        for opp in response.json()['results']:
            self.assertTrue(opp['isNew'])
            self.assertFalse(opp['alreadyVisited'])

    @requests_mock.Mocker()
    def test_opportunities_superuser_new_applicants(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        self.create_initial_scenario()

        opp = models.Opportunity.objects.filter_by__status_requested().filter(
            applicants__isnull=False).first()
        url = reverse('api:opportunity-admin', kwargs={'pk': opp.pk})
        response = self.client.get(url, data={})

        # INITIAL ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(opp.applicants.count(), response.data['newApplicants'])

        # DO ACTION a new applicant
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp.create_open_applicant(
            user, user, summary="")

        response = self.client.get(url, data={})
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(1, response.json()['newApplicants'])

    @requests_mock.Mocker()
    def test_opportunities_deleted(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        opp = self.create_opportunity()
        opp.remove(self.super_user)

        url = reverse('api:opportunity-list')

        # DO ACTION for admin
        response = self.client.get(url, data={'published_by_you': True})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], 0)

        # DO ACTION for regulra user
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], 0)
