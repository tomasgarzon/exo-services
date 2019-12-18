import requests_mock

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from datetime import timedelta
from rest_framework.test import APITestCase

from utils.test_mixin import (
    UserTestMixin,
    MockerTestMixin,
    request_mock_account,
)
from utils.faker_factory import faker

from ..models import Event
from .test_event_mixin import TestEventMixin


class TestApiSearchEvent(TestEventMixin, UserTestMixin, MockerTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_search_event(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        title_list = [
            'Test title {}'.format(faker.sentence()),
            'Test title {}'.format(faker.sentence()),
            'Test title {}'.format(faker.sentence()),
            'Faked title {}'.format(faker.sentence()),
            'Faked title {}'.format(faker.sentence()),
        ]
        for title in title_list:
            event = self.create_mommy_event(
                user=self.super_user,
                **{'start': timezone.now() + timedelta(days=3),
                   'title': title},
            )
            event.publish_event(self.super_user)
            self.create_mommy_participant(
                event,
                user=self.get_user(mock_user=True, is_consultant=True),
                user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
            )

        # DO ACTION
        response = self.client.get(
            '{}?search={}'.format(
                reverse('api:event:search'),
                'Test',
            )
        )

        # ASSERTIONS
        self.assertEqual(len(response.data), 3)

    @requests_mock.Mocker()
    def test_search_only_retrieve_public_events(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        events_status = [
            [settings.EVENT_CH_STATUS_PENDING, 3],
            [settings.EVENT_CH_STATUS_PUBLIC, 4],
            [settings.EVENT_CH_STATUS_DELETED, 2],
        ]
        for event_status in events_status:
            for _ in range(event_status[1]):
                event = self.create_mommy_event(
                    user=self.super_user,
                    **{'start': timezone.now() + timedelta(days=3),
                       '_status': event_status[0]},
                )
                self.create_mommy_participant(
                    event,
                    user=self.get_user(mock_user=True, is_consultant=True),
                    user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                )

        # DO ACTION & ASSERTIONS
        response = self.client.get(reverse('api:event:search'))

        # ASSERTIONS
        self.assertEqual(len(response.data), 4)

    @requests_mock.Mocker()
    def test_search_by_type_event(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        event_type_test_cases = [
            [settings.EXO_ROLE_CATEGORY_TALK, settings.EXO_ROLE_CODE_TALK_SPEAKER, 3],
            [settings.EXO_ROLE_CATEGORY_WORKSHOP, settings.EXO_ROLE_CODE_WORKSHOP_SPEAKER, 2],
            [settings.EXO_ROLE_CATEGORY_SUMMIT, settings.EXO_ROLE_CODE_SUMMIT_SPEAKER, 3],
            [settings.EXO_ROLE_CATEGORY_OTHER, settings.EXO_ROLE_CODE_OTHER_SPEAKER, 2],
        ]
        for test_case in event_type_test_cases:
            for _ in range(test_case[2]):
                event = self.create_mommy_event(
                    user=self.super_user,
                    category_code=test_case[0],
                    **{'start': timezone.now() + timedelta(days=3)},
                )
                event.publish_event(self.super_user)
                self.create_mommy_participant(
                    event,
                    user=self.get_user(mock_user=True, is_consultant=True),
                    user_role=test_case[1],
                )

        # DO ACTION & ASSERTIONS
        for test_case in event_type_test_cases:
            event_category = test_case[0]
            events_number = test_case[2]
            response = self.client.get(
                '{}?category={}'.format(
                    reverse('api:event:search'),
                    event_category,
                )
            )

            # ASSERTIONS
            self.assertEqual(len(response.data), events_number)

        # Test multiple types query
        response = self.client.get(
            '{}?category={}&category={}'.format(
                reverse('api:event:search'),
                settings.EXO_ROLE_CATEGORY_TALK,
                settings.EXO_ROLE_CATEGORY_OTHER,
            )
        )

        # ASSERTIONS
        self.assertEqual(len(response.data), 5)

    @requests_mock.Mocker()
    def test_search_by_follow_type(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        follow_type_test_cases = [
            [settings.EVENT_CH_FOLLOW_MODE_ON_SITE, 3, 3],
            [settings.EVENT_CH_FOLLOW_MODE_VIRTUAL, 2, 4],
            [settings.EVENT_CH_FOLLOW_MODE_STREAMING, 4, 8],
            [settings.EVENT_CH_FOLLOW_MODE_STREAMING, 4, 8],
            [settings.EVENT_CH_FOLLOW_MODE_VIRTUAL, 2, 4],
        ]

        for test_case in follow_type_test_cases:
            for _ in range(test_case[1]):
                event = self.create_mommy_event(
                    user=self.super_user,
                    **{'start': timezone.now() + timedelta(days=3),
                       'follow_type': test_case[0]},
                )
                event.publish_event(self.super_user)
                self.create_mommy_participant(
                    event,
                    user=self.get_user(mock_user=True, is_consultant=True),
                    user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                )

        # DO ACTION & ASSERTIONS
        for test_case in follow_type_test_cases:
            follow_type = test_case[0]
            total_events = test_case[2]
            response = self.client.get(
                '{}?follow_type={}'.format(
                    reverse('api:event:search'),
                    follow_type,
                )
            )

            # ASSERTIONS
            self.assertEqual(len(response.data), total_events)

    @requests_mock.Mocker()
    def test_search_by_language(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        spanish = 'Spanish'
        english = 'English'
        japanese = 'Japanese'

        languages_test_cases = [
            [[spanish], 3, 7],
            [[english], 4, 8],
            [[english, spanish], 2, 11],
            [[spanish, english], 2, 11],
            [[japanese], 0, 0],
        ]

        for test_case in languages_test_cases:
            for _ in range(test_case[1]):
                event = self.create_mommy_event(
                    user=self.super_user,
                    **{'start': timezone.now() + timedelta(days=3),
                       'languages': test_case[0]},
                )
                event.publish_event(self.super_user)
                self.create_mommy_participant(
                    event,
                    user=self.get_user(mock_user=True, is_consultant=True),
                    user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                )

        # DO ACTION & ASSERTIONS
        for test_case in languages_test_cases:
            languages = test_case[0]
            total_events = test_case[2]

            response = self.client.get(
                '{}?languages={}'.format(
                    reverse('api:event:search'),
                    ','.join(languages),
                )
            )

            # ASSERTIONS
            self.assertEqual(len(response.data), total_events)

    @requests_mock.Mocker()
    def test_search_by_location(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        spain = 'Spain'
        france = 'France'
        japan = 'Japan'

        location_test_cases = [
            [[spain], 3, 3],
            [[france], 4, 4],
            [[france, spain], 0, 7],
            [[spain, france], 0, 7],
            [[japan], 0, 0],
        ]
        for test_case in location_test_cases:
            location = test_case[0][0]
            for _ in range(test_case[1]):
                event = self.create_mommy_event(
                    user=self.super_user,
                    **{'start': timezone.now() + timedelta(days=3),
                       'location': location},
                )
                event.publish_event(self.super_user)
                self.create_mommy_participant(
                    event,
                    user=self.get_user(mock_user=True, is_consultant=True),
                    user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
                )

        # DO ACTION & ASSERTIONS
        for test_case in location_test_cases:
            locations = test_case[0]
            total_events = test_case[2]

            response = self.client.get(
                '{}?location={}'.format(
                    reverse('api:event:search'),
                    ','.join(locations),
                )
            )

            # ASSERTIONS
            self.assertEqual(len(response.data), total_events)

    @requests_mock.Mocker()
    def test_avoid_duplicated_events_on_list(self, mock_request):
        # PREPARE TEST
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        speaker_1 = self.get_user(mock_user=True, is_consultant=True)
        speaker_2 = self.get_user(mock_user=True, is_consultant=True)

        event = self.create_mommy_event(
            user=speaker_1,
            category_code=settings.EXO_ROLE_CATEGORY_OTHER,
            **{'start': timezone.now() + timedelta(days=3),
               'follow_type': settings.EVENT_CH_FOLLOW_MODE_VIRTUAL},
        )
        event.publish_event(self.super_user)
        self.create_mommy_participant(
            event,
            user=speaker_1,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
            **{'status': settings.EVENT_CH_ROLE_STATUS_ACTIVE,
               'order': 0},
        )
        self.create_mommy_participant(
            event,
            user=speaker_2,
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
            **{'status': settings.EVENT_CH_ROLE_STATUS_ACTIVE,
               'order': 0},
        )

        # DO ACTION
        response = self.client.get(reverse('api:event:search'))

        # ASSERTIONS
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(len(response.data), 1)
