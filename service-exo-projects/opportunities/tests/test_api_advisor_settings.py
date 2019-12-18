from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from project.faker_factories import FakeProjectFactory
from project.tests.test_mixin import ProjectTestMixin, request_mock_account


class AdvisorRequestSettingsAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_get_advisor_request_settings(self, mock_request):
        self.init_mock(mock_request)
        url = reverse(
            'api:project-advisor-request-settings',
            kwargs={'pk': self.project.pk})

        # ASSERTS
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data['total'])

    @requests_mock.Mocker()
    def test_modify_advisor_request_settings(self, mock_request):
        self.init_mock(mock_request)
        url = reverse(
            'api:project-advisor-request-settings',
            kwargs={'pk': self.project.pk})

        # ASSERTS
        self.setup_credentials(self.super_user)
        data = {
            'entity': faker.name(),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_HOUR,
            'duration_value': 1,
            'total': 10,
            'budgets': [
                {
                    'budget': '222',
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_DOLLAR
                }, {
                    'budget': '1',
                    'currency': settings.OPPORTUNITIES_CH_CURRENCY_EXOS
                }
            ],
        }
        response = self.client.put(url, data=data)
        self.assertTrue(status.is_success(response.status_code))
        advisor_request_settings = self.project.advisor_request_settings
        for key, value in data.items():
            self.assertEqual(
                getattr(advisor_request_settings, key),
                value)
