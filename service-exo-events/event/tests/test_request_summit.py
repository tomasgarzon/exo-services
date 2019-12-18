import requests_mock

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from utils.test_mixin import (
    UserTestMixin,
    MockerTestMixin,
    request_mock_account,
)
from utils.faker_factory import faker

from .test_event_mixin import TestEventMixin


class TestApiEvent(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        self.consultant_user = self.get_user(mock_user=True, is_consultant=True)

    @requests_mock.Mocker()
    @patch('event.tasks.events_tasks.SummitRequestTask.apply_async')
    def test_request_summit_creation(self, mock_request, mail_task):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.consultant_user)

        data = {'comment': faker.sentence()}
        url = reverse('api:event:event-request-summit')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mail_task.called)
