import requests_mock

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin

from .test_mixin import JobTestMixin, request_mock_account


class APIJobTest(
        UserTestMixin,
        JobTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_get_jobs(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=True)

        for _ in range(10):
            self.create_job(user)

        url = reverse('api:job-list')
        self.setup_credentials(user)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
