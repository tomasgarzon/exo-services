import requests_mock

from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin, MockerTestMixin
from utils.faker_factory import faker

from ..models import Interested
from .test_event_mixin import TestEventMixin


class EventInterestedTest(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()

    @requests_mock.Mocker()
    def test_event_interested_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        consultant = self.get_user(
            mock_user=True,
            is_consultant=True
        )
        event = self.create_mommy_event(
            user=consultant,
            category_code=settings.EXO_ROLE_CATEGORY_OTHER,
        )
        intereseted_data = {
            'name': faker.name(),
            'email': faker.email(),
            'event': event,
        }
        interested = Interested.objects.create(**intereseted_data)

        # DO ACTION
        url = reverse('api:event:interested-list', kwargs={'event_id': event.uuid.__str__()})
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0].get('name'), interested.name)
        self.assertEqual(response.json()[0].get('email'), interested.email)

    def test_event_interested_create(self):
        # PREPARE DATA
        consultant = self.get_user(
            mock_user=True,
            is_consultant=True
        )
        event = self.create_mommy_event(
            user=consultant,
            category_code=settings.EXO_ROLE_CATEGORY_SUMMIT,
        )
        data = {
            'name': faker.name(),
            'email': faker.email(),
            'event_id': event.pk,
        }

        # DO ACTION
        url = reverse('api:event:interested-create')
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json().get('name'), data.get('name'))
        self.assertEqual(response.json().get('email'), data.get('email'))
        self.assertEqual(response.json().get('event'), data.get('event'))
