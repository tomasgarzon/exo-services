import requests_mock

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import Permission

from utils.test_mixin import UserTestMixin, MockerTestMixin

from ..helpers.permission import EventPermissionHelper
from .test_event_mixin import TestEventMixin


class EventPermissionTest(TestEventMixin, UserTestMixin, MockerTestMixin, TestCase):

    def build_users(self):
        not_consultant = self.get_user(mock_user=True)

        regular_consultant = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(
            regular_consultant,
            {'certifications': []},
        )

        certified_ambassador_consultant = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(
            certified_ambassador_consultant,
            {'certifications': [{'code': settings.EVENT_AMBASSADOR_CERTIFICATION_CODE}]},
        )
        perm = Permission.objects.get(codename=settings.EVENT_PERMS_CREATE_EVENT_SUMMIT)
        certified_ambassador_consultant.user_permissions.add(perm)

        certified_coach_consultant = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(
            certified_coach_consultant,
            {'certifications': [{'code': settings.EVENT_COACH_CERTIFICATION_CODE}]},
        )

        certified_foundations_consultant = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(
            certified_foundations_consultant,
            {'certifications': [{'code': settings.EVENT_FOUNDATIONS_CERTIFICATION_CODE}]},
        )

        certified_trainer_consultant = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(
            certified_trainer_consultant,
            {'certifications': [{'code': settings.EVENT_TRAINER_CERTIFICATION_CODE}]},
        )

        return [
            not_consultant,
            regular_consultant,
            certified_ambassador_consultant,
            certified_coach_consultant,
            certified_trainer_consultant,
            certified_foundations_consultant,
        ]

    def test_user_with_permission_can_publish_event(self):
        # PREPARE DATA
        event_manager_user = self.get_user(mock_user=True, is_consultant=True)
        self.update_user_mock(
            event_manager_user,
            {'certifications': []},
        )
        perm = Permission.objects.get(codename=settings.EVENT_PERMS_MANAGE_EVENT)
        event_manager_user.user_permissions.add(perm)
        regular_consultant = self.get_user(
            mock_user=True,
            is_consultant=True
        )
        event = self.create_mommy_event(
            user=regular_consultant,
            category_code=settings.EXO_ROLE_CATEGORY_TALK,
        )

        # DO ACTION
        event.status = (event_manager_user, settings.EVENT_CH_STATUS_PUBLIC)

        # ASSERTIONS
        self.assertTrue(event.status, settings.EVENT_CH_STATUS_PUBLIC)
        self.assertTrue(
            event_manager_user.user_permissions.filter(
                codename=settings.EVENT_PERMS_MANAGE_EVENT
            ).exists()
        )

    def test_user_without_permission_can_not_publish_event(self):
        # PREPARE DATA
        regular_consultant = self.get_user(
            mock_user=True,
            is_consultant=True
        )
        event = self.create_mommy_event(
            user=regular_consultant,
            category_code=settings.EXO_ROLE_CATEGORY_TALK,
        )

        # DO ACTION
        with self.assertRaises(AssertionError):
            event.status = (regular_consultant, settings.EVENT_CH_STATUS_PUBLIC)

            # ASSERTIONS
            self.assertTrue(event.status, settings.EVENT_CH_STATUS_PENDING)
            self.assertFalse(
                regular_consultant.user_permissions.filter(
                    codename=settings.EVENT_PERMS_MANAGE_EVENT
                ).exists()
            )

    def test_event_owner_can_edit(self):
        # PREPARE DATA
        consultant = self.get_user(
            mock_user=True,
            is_consultant=True
        )

        # DO ACTION
        event = self.create_mommy_event(
            user=consultant,
            category_code=settings.EXO_ROLE_CATEGORY_TALK,
        )

        # ASSERTIONS
        self.assertTrue(
            consultant.has_perm(
                settings.EVENT_PERMS_EDIT_EVENT,
                event,
            )
        )

    @requests_mock.Mocker()
    def test_permission_to_create_talks(self, mock_request):
        self.init_mock(mock_request)

        users = self.build_users()

        test_cases = [
            {'user': users[0], 'can_create': False},
            {'user': users[1], 'can_create': False},
            {'user': users[2], 'can_create': True},
            {'user': users[3], 'can_create': True},
            {'user': users[4], 'can_create': True},
            {'user': users[5], 'can_create': True},
        ]

        for case in test_cases:
            event_permission_helper = EventPermissionHelper()

            # DO ACTION
            can_create_talk = event_permission_helper.has_perm(
                case.get('user'),
                'create_{}'.format(settings.EXO_ROLE_CATEGORY_TALK),
            )

            # ASSERTIONS
            self.assertEqual(can_create_talk, case.get('can_create'))

    @requests_mock.Mocker()
    def test_permission_to_create_event_type_other(self, mock_request):
        self.init_mock(mock_request)

        users = self.build_users()

        test_cases = [
            {'user': users[0], 'can_create': False},
            {'user': users[1], 'can_create': True},
            {'user': users[2], 'can_create': True},
            {'user': users[3], 'can_create': True},
            {'user': users[4], 'can_create': True},
            {'user': users[5], 'can_create': True},
        ]

        for case in test_cases:
            event_permission_helper = EventPermissionHelper()

            # DO ACTION
            can_create_events_type_other = event_permission_helper.has_perm(
                case.get('user'),
                'create_{}'.format(settings.EXO_ROLE_CATEGORY_OTHER),
            )

            # ASSERTIONS
            self.assertEqual(can_create_events_type_other, case.get('can_create'))

    @requests_mock.Mocker()
    def test_permission_to_create_workshops(self, mock_request):
        self.init_mock(mock_request)

        users = self.build_users()

        test_cases = [
            {'user': users[0], 'can_create': False},
            {'user': users[1], 'can_create': False},
            {'user': users[2], 'can_create': False},
            {'user': users[3], 'can_create': False},
            {'user': users[4], 'can_create': True},
            {'user': users[5], 'can_create': False},
        ]

        for case in test_cases:
            event_permission_helper = EventPermissionHelper()

            # DO ACTION
            can_create_workshop = event_permission_helper.has_perm(
                case.get('user'),
                'create_{}'.format(settings.EXO_ROLE_CATEGORY_WORKSHOP),
            )

            # ASSERTIONS
            self.assertEqual(can_create_workshop, case.get('can_create'))

    @requests_mock.Mocker()
    def test_permission_to_create_summits(self, mock_request):
        self.init_mock(mock_request)

        users = self.build_users()

        test_cases = [
            {'user': users[0], 'can_create': False},
            {'user': users[1], 'can_create': False},
            {'user': users[2], 'can_create': True},
            {'user': users[3], 'can_create': False},
            {'user': users[4], 'can_create': False},
            {'user': users[5], 'can_create': False},
        ]

        for case in test_cases:
            event_permission_helper = EventPermissionHelper()

            # DO ACTION
            can_create_summit = event_permission_helper.has_perm(
                case.get('user'),
                'create_{}'.format(settings.EXO_ROLE_CATEGORY_SUMMIT),
            )

            # ASSERTIONS
            self.assertEqual(can_create_summit, case.get('can_create'))
