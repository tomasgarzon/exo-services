import requests_mock

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import (
    UserTestMixin,
    MockerTestMixin,
    request_mock_account,
)

from ..conf import settings
from .test_event_mixin import TestEventMixin


class TestPublicEventApi(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user,
            is_consultant=False,
            is_superuser=True)

    @requests_mock.Mocker()
    def test_get_event_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        user = self.get_user(mock_user=True, is_consultant=True)
        request_mock_account.add_mock(
            user,
            is_consultant=False,
            is_superuser=True)

        event = self.create_mommy_event(user=user)

        user1 = self.get_user(mock_user=True, is_consultant=True)
        request_mock_account.add_mock(
            user1,
            is_consultant=False,
            is_superuser=True)
        self.create_mommy_participant(
            event,
            user=user1,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )
        url = reverse('api:event:public', kwargs={'event_id': event.uuid.__str__()})

        # DO ACTION
        response = self.client.get(url, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
