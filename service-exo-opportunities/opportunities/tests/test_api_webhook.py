from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin

from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityWebhookAPITestCase(
        UserTestMixin, OpportunityTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_super_user()
        self.setup_username_credentials()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_first_message(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        opp = self.create_opportunity()
        url = reverse('api:webhook-first-message')
        data = {
            'message': faker.text(),
            'created_by_uuid': opp.created_by.uuid.__str__(),
            'other_user_uuid': user.uuid.__str__(),
            'opportunity_uuid': opp.uuid.__str__(),
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
