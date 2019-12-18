import uuid
import requests_mock

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account
from ..faker_factories import FakeOpportunityGroupFactory
from .. import models


class OpportunityAPITest(
        UserTestMixin,
        MagicMockMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)
        self.team_uuid = uuid.uuid4().__str__()
        for _ in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user,
                is_consultant=False,
                is_superuser=False,
            )
        self.group = FakeOpportunityGroupFactory.create(
            budgets=[
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EUR,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
                {
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS,
                    'budget': '{}.0'.format(int(faker.numerify()))
                },
            ],
            total=3,
            related_uuid=self.team_uuid)
        for _ in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user,
                is_consultant=False,
                is_superuser=False,
            )
            self.group.managers.add(user)
        self.user1 = self.group.managers.all()[0]
        self.user2 = self.group.managers.all()[1]

    @requests_mock.Mocker()
    def test_list_opportunities_group(self, mock_request):
        # PREPARE DATA
        TOTAL_OPPORTUNITIES = 4
        self.init_mock(mock_request)
        url = reverse(
            'api:opportunity-group-list',
            kwargs={'group_id': self.group.id})
        url += '?published_by_you=True'
        for _ in range(TOTAL_OPPORTUNITIES):
            self.create_opportunity(self.user1, group=self.group)

        for user in self.group.managers.all():
            # DO ACTION
            self.setup_credentials(user)
            response = self.client.get(url)
            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
            self.assertEqual(
                response.json()['count'], TOTAL_OPPORTUNITIES)
            for value in response.json()['results']:
                self.assertEqual(len(value['userActions']), 4)

    @requests_mock.Mocker()
    def test_create_opportunities_group(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user1)
        data = self.get_api_data()
        url = reverse('api:opportunity-list')
        data['group'] = self.group.id

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp_data = response.json()
        self.assertEqual(opp_data['entity'], self.group.entity)
        self.assertEqual(opp_data['budgets'], self.group.budgets)
        self.assertEqual(opp_data['exoRole'], self.group.exo_role.code)
        self.assertEqual(self.group.opportunities.count(), 1)

    @requests_mock.Mocker()
    def test_validate_total_opportunities_group(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user1)
        data = self.get_api_data()
        data['num_positions'] = 4
        data['group'] = self.group.id
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @requests_mock.Mocker()
    def test_validate_total_opportunities_group_updating(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user1)
        self.group.total = 5
        self.group.save()
        self.create_opportunity(user=self.user1, group=self.group)
        opp = self.create_opportunity(
            user=self.user1, num_positions=2, group=self.group)

        # DO ACTION increase positions
        response = self.group.has_positions_availables(3, opp)

        # ASSERTS
        self.assertFalse(response)

        # DO ACTION decrease positions
        response = self.group.has_positions_availables(1, opp)

        # ASSERTS
        self.assertTrue(response)

    @requests_mock.Mocker()
    def test_owner_admin_retrieve_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(self.user1, group=self.group)
        for _ in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})
        self.setup_credentials(self.user2)

        # DO ACTION
        response = self.client.get(url)
        data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNone(data['myApplicant'])
        self.assertEqual(len(data['applicants']), 3)
        self.assertIsNotNone(data['requestedBy'])

    @requests_mock.Mocker()
    def test_update_request_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(user=self.user1, group=self.group)
        self.setup_credentials(self.user2)
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})
        response = self.client.get(url)
        data = response.json()
        data['title'] = faker.word()
        data['exoRole'] = data['exoRole']['code']
        data['certificationRequired'] = data['certificationRequired']['code']
        # DO ACTION
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})

        response = self.client.put(
            url, data=data, **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertEqual(opp.group, self.group)

    @requests_mock.Mocker()
    def test_close_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(user=self.user1, group=self.group)

        url = reverse(
            'api:opportunity-close',
            kwargs={'pk': opp.pk})

        # DO ACTION
        self.setup_credentials(self.user2)
        response = self.client.put(
            url, data={'comment': faker.text()},
            **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_closed)

    @requests_mock.Mocker()
    def test_remove_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(user=self.user1, group=self.group)

        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})

        # DO ACTION
        self.setup_credentials(self.user2)
        response = self.client.delete(
            url, **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_removed)

    @requests_mock.Mocker()
    def test_assign_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(user=self.user1, group=self.group)
        self.setup_credentials(self.user2)

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
            self.assertTrue(status.is_success(response.status_code))
