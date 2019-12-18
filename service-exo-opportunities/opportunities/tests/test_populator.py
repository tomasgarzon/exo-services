from django.urls import reverse
from django.test import override_settings
from django.core import management
from django.utils.six import StringIO
from django.contrib.auth import get_user_model

import requests_mock

from rest_framework import status
from rest_framework.test import APITransactionTestCase

from utils.test_mixin import UserTestMixin

from .test_mixin import OpportunityTestMixin, request_mock_account


@override_settings(POPULATOR_MODE=True)
class OpportunityPopulatorTest(
        UserTestMixin,
        OpportunityTestMixin,
        APITransactionTestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def retrieve_opportunity(self, pk):
        url = reverse('api:opportunity-detail', kwargs={'pk': pk})
        response = self.client.get(url, data={})
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_opportunities_consultant_from_populator(self, mock_request):
        # PREPARE DATA
        out = StringIO()
        err = StringIO()
        self.init_mock(mock_request)
        users = [
            '0737a9f9_22a0_4286_8be3_34a3e19d92dc',
            '299c8c8a_4e4a_4c6b_904a_1b801b7227f1',
            '7749ad25_5128_4644_895f_6b9a70b605bd',
            '1cd07dd7_4883_4838_9b5a_303ef0d6580c',
            '47b10a71_d011_48c2_b359_2a2027191fd8',
            'ef70053f_755b_4b40_bb73_6832d16488e7',
            '1eae2bfa_3b44_4e3a_8bb7_89f5e24c71a6',
            '1da6e073-a525-4311-ab7e-ec8748d76100',
            'eb926b17-634c-477d-847c-eda5f35026a2',
            '5c197c35-5e7e-4006-b272-0fb1e8628404',
            '5d640164-b7a3-4936-b37e-3ad5a23a2036',
            '5ec7b001_37a4_4bd4_95e3_d780377ed294',
            '85227667-5866-4567-b820-57806d00932c',
            'a71654e1-ff04-458a-b869-af2eaa710e83']
        for user_uuid in users:
            user = get_user_model().objects.create(
                uuid=user_uuid.replace('_', '-'))
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
        management.call_command('populate', stdout=out, stderr=err)

        gorka_user = get_user_model().objects.get(
            uuid='1eae2bfa-3b44-4e3a-8bb7-89f5e24c71a6')
        self.setup_credentials(gorka_user)
        self.add_marketplace_permission(gorka_user)
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.get(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], 3)
        for opp in response.json()['results']:
            self.retrieve_opportunity(opp['pk'])
