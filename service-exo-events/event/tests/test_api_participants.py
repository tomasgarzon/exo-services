import requests_mock
import uuid

from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from unittest import mock
from unittest.mock import patch
from datetime import timedelta

from utils.test_mixin import (
    UserTestMixin,
    MockerTestMixin,
    request_mock_account,
)
from utils.faker_factory import faker
from certification.signals_define import (
    create_certification_credential)
from certification.models import CertificationGroup

from ..conf import settings
from .test_event_mixin import TestEventMixin


class User:
    uuid = None

    def __init__(self):
        self.uuid = uuid.uuid4()


class TestApiParticipants(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user,
            is_consultant=False,
            is_superuser=True)
        self.event = self.create_mommy_event(
            user=self.super_user,
            category_code=settings.EXO_ROLE_CATEGORY_SUMMIT,
            **{'start': timezone.now().date() - timedelta(days=2),
               'end': timezone.now().date() - timedelta(days=1)}
        )
        self.event.publish_event(self.super_user)

    @requests_mock.Mocker()
    def test_add_participant_with_uuid(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        user = User()
        request_mock_account.add_mock(
            user,
            is_consultant=True,
            is_superuser=False)
        data = {
            'uuid': user.uuid.__str__(),
            'full_name': faker.name(),
            'email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SUMMIT_SPEAKER
        }

        url = reverse(
            'api:event:participant-list',
            kwargs={'event_id': self.event.uuid.__str__()})

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.event.participants.count(), 1)
        participant = self.event.participants.first()
        self.assertEqual(participant.user.uuid, user.uuid)
        self.assertTrue(participant.is_speaker)

    @requests_mock.Mocker()
    def test_add_participant_without_uuid(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        data = {
            'full_name': faker.name(),
            'user_email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
        }

        url = reverse(
            'api:event:participant-list',
            kwargs={'event_id': self.event.uuid.__str__()})

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.event.participants.count(), 1)
        participant = self.event.participants.first()
        self.assertIsNotNone(participant.user)
        self.assertTrue(participant.is_participant)

    @requests_mock.Mocker()
    def test_update_participant_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        self.create_mommy_participant(
            self.event,
            user=self.get_user(mock_user=True, is_consultant=True),
            user_role=settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
        )
        data = {
            'full_name': faker.name(),
            'user_email': faker.email(),
        }
        participant = self.event.participants.first()
        previous_user = participant.user
        url = reverse(
            'api:event:participant-detail',
            kwargs={
                'event_id': self.event.uuid.__str__(),
                'pk': participant.pk})

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        participant.refresh_from_db()
        self.assertEqual(participant.user_name, data['full_name'])
        self.assertEqual(participant.user_email, data['user_email'])
        self.assertEqual(participant.user, previous_user)

    @requests_mock.Mocker()
    def test_delete_participant_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        self.create_mommy_participant(
            self.event,
            user=self.get_user(mock_user=True, is_consultant=True),
            user_role=settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
        )
        participant = self.event.participants.first()
        url = reverse(
            'api:event:participant-detail',
            kwargs={
                'event_id': self.event.uuid.__str__(),
                'pk': participant.pk})

        # DO ACTION
        response = self.client.delete(url, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.event.participants.count(), 0)

    @requests_mock.Mocker()
    def test_upload_members(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        url = reverse(
            'api:event:participant-upload',
            kwargs={'event_id': self.event.uuid.__str__()},
        )
        content = ''
        for k in range(10):
            full_name = '{} {}'.format(faker.first_name(), faker.last_name())
            content += '{},{}\n'.format(full_name, faker.email())

        data = {
            'content': content,
            'exo_role': settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
        }

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 10)
        self.assertEqual(self.event.participants.count(), 10)

    @requests_mock.Mocker()
    @patch('certification.accredible.credentials.create_simple_credential')
    def test_generate_participant_list(self, mock_request, mock_credential):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        handler = mock.Mock()
        create_certification_credential.connect(handler)
        self.create_mommy_participant(
            self.event,
            user=self.get_user(mock_user=True, is_consultant=True),
            user_role=settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
        )
        ct = ContentType.objects.get_for_model(self.event)
        CertificationGroup.objects.create(
            content_type=ct,
            object_id=self.event.pk)
        participant = self.event.participants.first()
        url = reverse(
            'api:event:participant-generate-certificate',
            kwargs={
                'event_id': self.event.uuid.__str__(),
                'pk': participant.pk})

        # DO ACTION
        response = self.client.post(url, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(handler.called)
        self.assertTrue(mock_credential)
        create_certification_credential.disconnect(handler)

    @requests_mock.Mocker()
    def test_participant_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        for _ in range(2):
            self.create_mommy_participant(
                self.event,
                user=self.get_user(mock_user=True, is_consultant=True),
                user_role=settings.EXO_ROLE_CODE_SUMMIT_SPEAKER,
            )
        for _ in range(10):
            self.create_mommy_participant(
                self.event,
                user=self.get_user(mock_user=True, is_consultant=True),
                user_role=settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
            )

        self.setup_credentials(self.event.participants.first().user)
        url = reverse(
            'api:event:participant-list',
            kwargs={'event_id': self.event.uuid.__str__()})

        # DO ACTION
        response = self.client.get(url, format='json')

        # ASSERTS

        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.event.participants.count(), 12)
        self.assertEqual(len(response.data), 12)

    @requests_mock.Mocker()
    def test_participant_badges_list_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        for _ in range(2):
            self.create_mommy_participant(
                self.event,
                user=self.get_user(mock_user=True, is_consultant=True),
                user_role=settings.EXO_ROLE_CODE_SUMMIT_SPEAKER,
            )
        for _ in range(10):
            self.create_mommy_participant(
                self.event,
                user=self.get_user(mock_user=True, is_consultant=True),
                user_role=settings.EXO_ROLE_CODE_SUMMIT_PARTICIPANT,
            )

        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url = reverse('api:event:participant-badges')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.event.participants.count(), 12)
        self.assertEqual(len(response.json()), 2)

    @requests_mock.Mocker()
    def test_add_participant_from_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_username_credentials()
        user = User()
        request_mock_account.add_mock(
            user,
            is_consultant=True,
            is_superuser=False)

        data = {
            'user': user.uuid.__str__(),
            'user_from': self.event.created_by.uuid.__str__(),
            'exoRole': settings.EXO_ROLE_CODE_SUMMIT_SPEAKER,
            'opportunity_uuid': uuid.uuid4().__str__(),
        }

        url = reverse(
            'api:event:participant-add-from-opportunity',
            kwargs={'event_id': self.event.uuid.__str__()})

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.event.participants.count(), 1)
        participant = self.event.participants.first()
        self.assertEqual(participant.user.uuid, user.uuid)
        self.assertTrue(participant.is_speaker)
