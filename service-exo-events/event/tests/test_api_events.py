import random
import requests_mock

from django.db.models.signals import pre_delete
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone

from datetime import datetime
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch, Mock

from certification.models import CertificationGroup
from utils.test_mixin import (
    UserTestMixin,
    MockerTestMixin,
    request_mock_account,
)
from utils.faker_factory import faker

from ..models import Event, Organizer
from ..conf import settings
from .test_event_mixin import TestEventMixin


class TestApiEvent(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user,
            is_consultant=False,
            is_superuser=True)
        self.consultant_user = self.get_user(mock_user=True, is_consultant=True)

    @requests_mock.Mocker()
    def test_create_event_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.consultant_user)

        custom_event_type = faker.word()
        data = {
            'title': faker.sentence(),
            'sub_title': faker.sentence(),
            'description': faker.text(),
            'start': timezone.now().date(),
            'end': timezone.now().date(),
            'category': settings.EXO_ROLE_CATEGORY_OTHER,
            'type_event_name': custom_event_type,
            'follow_type': 'V',
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'url': faker.uri(),
            'event_image': faker.uri(),
            'languages': [faker.word()],
            'show_price': faker.boolean(),
            'amount': faker.numerify(),
            'currency': [*dict(settings.EVENT_CURRENCY_CHOICES).keys()][random.randint(0, 1)],
            'organizers': [
                {
                    'name': faker.name(),
                    'email': faker.email(),
                    'url': faker.uri()
                },
            ],
            'participants': []
        }

        url = reverse('api:event:api-root')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        event = Event.objects.first()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(Event.objects.count(), 1)
        self.assertTrue(Event.objects.first().is_pending)
        self.assertEqual(str(event.uuid), response.data.get('uuid'))
        self.assertEqual(event.created_by, self.consultant_user)
        self.assertEqual(response.json().get('typeEventName'), custom_event_type)
        self.assertEqual(Organizer.objects.count(), 1)

    @requests_mock.Mocker()
    def test_edit_event_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        event = self.create_mommy_event(user=self.consultant_user)
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(self.consultant_user)

        new_title = faker.sentence()
        data = {
            'title': new_title,
            'sub_title': event.sub_title,
            'description': event.description,
            'start': event.start,
            'end': event.end,
            'category': event.category.code,
            'follow_type': event.follow_type,
            'location': event.location,
            'url': event.url,
            'languages': event.languages,
            'show_price': event.show_price,
            'amount': event.amount,
            'currency': event.currency,
            'organizers': [],
            'participants': [],
        }
        url = reverse('api:event:event-detail', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(url, data=data, format='json')
        event.refresh_from_db()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(event.title, new_title)

    @requests_mock.Mocker()
    def test_event_change_status_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        mock_delete_handler = Mock()
        pre_delete.connect(mock_delete_handler, sender=Event)

        event = self.create_mommy_event(user=self.consultant_user)
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(self.consultant_user)

        event_obj = Event.objects.get(uuid=event.uuid)
        url = reverse('api:event:event-change-status', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(
            url,
            data={'status': settings.EVENT_CH_STATUS_DELETED},
            format='json',
        )
        event_obj.refresh_from_db()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(event_obj.is_deleted)
        self.assertTrue(mock_delete_handler.called)

    @requests_mock.Mocker()
    def test_list_my_events_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        speaker_1 = self.get_user(mock_user=True, is_consultant=True)
        speaker_2 = self.get_user(mock_user=True, is_consultant=True)
        speaker_3 = self.get_user(mock_user=True, is_consultant=True)

        test_cases = [
            {'speaker': speaker_1, 'events': 3},
            {'speaker': speaker_2, 'events': 4},
            {'speaker': speaker_3, 'events': 2},
            {'speaker': self.super_user, 'events': 4},
        ]
        test_environ = [
            {'event': self.create_mommy_event(user=self.super_user),
             'speakers': [speaker_1, speaker_2],
             },
            {'event': self.create_mommy_event(user=self.super_user),
             'speakers': [speaker_2, speaker_1, speaker_3],
             },
            {'event': self.create_mommy_event(user=self.super_user),
             'speakers': [speaker_3, speaker_1, speaker_2],
             },
            {'event': self.create_mommy_event(user=self.super_user),
             'speakers': [speaker_2],
             },
        ]

        for test_case in test_environ:
            event = test_case.get('event')
            speakers = test_case.get('speakers')
            for participant_order, participant in enumerate(speakers):
                extra_params = {'order': participant_order, 'status': settings.EVENT_CH_ROLE_STATUS_ACTIVE}
                self.create_mommy_participant(
                    event,
                    user=participant,
                    user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                    **extra_params,
                )

        url = reverse('api:event:api-root')

        # DO ACTION
        for test_case in test_cases:
            speaker = test_case.get('speaker')
            speaker_events = test_case.get('events')

            self.setup_credentials(speaker)
            response = self.client.get(url)

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
            self.assertEqual(len(response.data), speaker_events)

    @requests_mock.Mocker()
    def test_create_participants_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.consultant_user)

        data = {
            'title': faker.sentence(),
            'sub_title': faker.sentence(),
            'description': faker.text(),
            'start': timezone.now().date(),
            'end': timezone.now().date(),
            'category': settings.EXO_ROLE_CATEGORY_OTHER,
            'follow_type': 'P',
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'url': faker.uri(),
            'languages': [faker.word()],
            'show_price': faker.boolean(),
            'amount': faker.numerify(),
            'currency': [*dict(settings.EVENT_CURRENCY_CHOICES).keys()][random.randint(0, 1)],
            'organizers': [
                {
                    'name': faker.name(),
                    'email': faker.email(),
                    'url': faker.uri()
                },
            ],
            'participants': [
                {
                    'uuid': self.consultant_user.uuid.__str__(),
                    'exo_role': settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                    'order': 1,
                }
            ]
        }

        url = reverse('api:event:api-root')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        event = Event.objects.first()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(event.participants.count(), 1)

    @requests_mock.Mocker()
    def test_edit_participants_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        event = self.create_mommy_event(
            user=self.super_user,
            category_code=settings.EXO_ROLE_CATEGORY_OTHER,
        )
        participant = self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(self.consultant_user)

        consultant_user = self.get_user(mock_user=True, is_consultant=True)

        data = {
            'title': event.title,
            'sub_title': event.sub_title,
            'description': event.description,
            'start': event.start,
            'end': event.end,
            'category': event.category.code,
            'follow_type': event.follow_type,
            'location': event.location,
            'url': event.url,
            'languages': event.languages,
            'show_price': event.show_price,
            'amount': event.amount,
            'currency': event.currency,
            'organizers': [],
            'participants': [
                {
                    'uuid': participant.user.uuid,
                    'exo_role': settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                    'order': 2,
                },
                {
                    'uuid': consultant_user.uuid,
                    'exo_role': settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                    'order': 1,
                },

            ]
        }

        url = reverse('api:event:event-detail', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(event.participants.count(), 2)
        self.assertEqual(
            event.participants.get(order=1).user,
            consultant_user
        )

    @requests_mock.Mocker()
    def test_retrieve_event(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        event = self.create_mommy_event(user=self.super_user)
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )
        self.setup_credentials(self.consultant_user)
        url = reverse('api:event:event-detail', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.get(url, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data['participants']), 1)

    @requests_mock.Mocker()
    @patch('certification.models.CertificationGroup.objects.release_group_credential')
    def test_generate_participant_list(self, mock_request, mock_credential):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        event = self.create_mommy_event(user=self.super_user)
        ct = ContentType.objects.get_for_model(event)
        CertificationGroup.objects.create(
            content_type=ct,
            object_id=event.pk)
        for _ in range(5):
            self.create_mommy_participant(
                event,
                user=self.get_user(mock_user=True, is_consultant=True),
                user_role=settings.EXO_ROLE_CODE_OTHER_PARTICIPANT,
            )

        url = reverse(
            'api:event:event-send-certificates',
            kwargs={
                'uuid': event.uuid.__str__()})

        # DO ACTION
        response = self.client.post(url, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_credential.called)

    @requests_mock.Mocker()
    @patch('event.tasks.events_tasks.EventUpdatedOwnerNotificationTask.apply_async')
    def test_user_with_permission_can_make_event_public(self, mock_request, mock_task):
        self.init_mock(mock_request)

        event_manager_user = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(event_manager_user, {'certifications': []})
        perm = Permission.objects.get(codename=settings.EVENT_PERMS_MANAGE_EVENT)
        event_manager_user.user_permissions.add(perm)
        event = self.create_mommy_event(
            user=self.consultant_user,
            **{'start': datetime.now().date()},
        )
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(event_manager_user)

        url = reverse('api:event:event-publish', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(url, data={'comments': ''}, format='json')

        # ASSERTIONS
        event.refresh_from_db()
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertEqual(event.status, settings.EVENT_CH_STATUS_PUBLIC)
        self.assertTrue(mock_task.called)

    @requests_mock.Mocker()
    def test_user_without_permission_can_not_event_public(self, mock_request):
        self.init_mock(mock_request)

        event = self.create_mommy_event(
            user=self.consultant_user,
            category_code=settings.EXO_ROLE_CATEGORY_OTHER,
        )
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(self.consultant_user)
        url = reverse('api:event:event-publish', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(url, data={'comments': ''}, format='json')

        # ASSERTIONS
        event.refresh_from_db()
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(event.status, settings.EVENT_CH_STATUS_PENDING)

    @requests_mock.Mocker()
    @patch('event.tasks.events_tasks.EventUpdatedOwnerNotificationTask.apply_async')
    def test_user_with_permission_can_reject_event(self, mock_request, mock_task):
        self.init_mock(mock_request)

        event_manager_user = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(event_manager_user, {'certifications': []})
        perm = Permission.objects.get(codename=settings.EVENT_PERMS_MANAGE_EVENT)
        event_manager_user.user_permissions.add(perm)

        event = self.create_mommy_event(
            user=self.consultant_user,
            category_code=settings.EXO_ROLE_CATEGORY_OTHER,
            **{'start': datetime.now().date()},
        )
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(event_manager_user)

        url = reverse('api:event:event-reject', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(url, data={'comments': ''}, format='json')

        # ASSERTIONS
        event.refresh_from_db()
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertEqual(event.status, settings.EVENT_CH_STATUS_UNDER_REVIEW)
        self.assertTrue(mock_task.called)

    @requests_mock.Mocker()
    def test_user_without_permission_can_not_reject_event(self, mock_request):
        self.init_mock(mock_request)

        event = self.create_mommy_event(
            user=self.consultant_user,
            category_code=settings.EXO_ROLE_CATEGORY_OTHER,
            **{'start': datetime.now().date()},
        )
        self.create_mommy_participant(
            event,
            user=self.consultant_user,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        self.setup_credentials(self.consultant_user)

        url = reverse('api:event:event-reject', kwargs={'uuid': event.uuid})

        # DO ACTION
        response = self.client.put(url, data={'comments': ''}, format='json')

        # ASSERTIONS
        event.refresh_from_db()
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(event.status, settings.EVENT_CH_STATUS_PENDING)
