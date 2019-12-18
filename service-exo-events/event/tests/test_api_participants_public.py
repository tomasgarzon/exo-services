from django.conf import settings
from django.urls import reverse

from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin, MockerTestMixin
from utils.faker_factory import faker

from .test_event_mixin import TestEventMixin


class TestAPIParticipantsPublic(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()

    @patch('event.tasks.sync_participant_task.SyncParticipantTask.apply_async')
    def test_event_participant_public_create(self, mock_task):
        # PREPARE DATA
        url = reverse('api:event:participant-public-create')

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
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(
            event.participants
            .filter_by_email(data.get('email'))
            .filter_by_role_name(settings.EVENT_PARTICIPANT_NAME)
            .exists()
        )
        self.assertTrue(mock_task.called)
        self.assertEqual(mock_task.call_count, 1)

        self.assertIsNotNone(event.participants.first().job)
