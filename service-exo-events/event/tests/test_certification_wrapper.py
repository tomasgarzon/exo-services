import requests_mock

from django.conf import settings
from django.test import TestCase

from unittest.mock import patch

from utils.test_mixin import (
    UserTestMixin,
    MockerTestMixin,
    request_mock_account,
)
from utils.faker_factory import faker
from utils.certification_helpers import CertificationWorkshopWrapper
from certification.signals_define import create_certification_group

from .test_event_mixin import TestEventMixin


class TestCertificationWrapper(TestEventMixin, UserTestMixin, MockerTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    @patch('certification.accredible.groups.create_group')
    def test_create(self, mock_request, mock_create):
        # PREPARE TEST
        self.init_mock(mock_request)

        event = self.create_mommy_event(
            user=self.super_user,
            **{'title': 'Test title {}'.format(faker.sentence())},
        )
        self.create_mommy_participant(
            event,
            user=self.get_user(mock_user=True, is_consultant=True),
            user_role=settings.EXO_ROLE_CODE_OTHER_SPEAKER,
        )

        # DO ACTION
        event_wrapper = CertificationWorkshopWrapper(event)
        create_certification_group.send(
            sender=event.__class__,
            **event_wrapper.get_data(event.created_by),
        )

        # ASSERTIONS
        self.assertTrue(mock_create.called)
        self.assertIsNotNone(
            event_wrapper.get_data(event.created_by).get('instructor_name')
        )
