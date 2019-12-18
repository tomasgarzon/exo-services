from django.test import TestCase
from django.conf import settings

import requests_mock
from unittest import mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account
from ..signals_define import opportunity_post_closed, opportunity_positions_covered


class OpportunityActionCloseTest(
        UserTestMixin,
        OpportunityTestMixin,
        MagicMockMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_close_manually_opportunity_with_applicants(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        handler = mock.Mock()
        opportunity_post_closed.connect(handler)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        comment = faker.text()
        user_conversation = self.get_user()
        opp.start_conversation(user_conversation, faker.text(), [])

        # DO ACTION
        opp.close(self.super_user, comment)

        # ASSERTS
        self.assertTrue(opp.is_closed)
        self.assertEqual(
            opp.applicants_info.filter_by_status_selected().count(),
            1)
        self.assertEqual(opp.closed_by.user, self.super_user)
        self.assertEqual(handler.call_count, 1)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'comment'),
            comment)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'origin'),
            settings.OPPORTUNITIES_CH_CLOSE_MANUALLY)
        self.assertEqual(
            set(self.get_mock_kwarg(handler, 'user_list')),
            {user_conversation})
        opportunity_post_closed.disconnect(handler)

    @requests_mock.Mocker()
    def test_close_positions_covered_opportunity_with_applicants(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        handler = mock.Mock()
        opportunity_post_closed.connect(handler)

        # DO ACTION
        opportunity_positions_covered.send(
            sender=opp.__class__, opportunity=opp)

        # ASSERTS
        self.assertTrue(opp.is_closed)
        self.assertEqual(
            opp.applicants_info.filter_by_status_selected().count(),
            0)
        self.assertEqual(opp.closed_by.user, None)
        self.assertEqual(handler.call_count, 1)
        self.assertIsNone(
            self.get_mock_kwarg(handler, 'comment'),
        )
        self.assertEqual(
            self.get_mock_kwarg(handler, 'origin'),
            settings.OPPORTUNITIES_CH_CLOSE_POSITIONS)
        opportunity_post_closed.disconnect(handler)

    @requests_mock.Mocker()
    def test_close_deadline_covered_opportunity_with_applicants(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        handler = mock.Mock()
        opportunity_post_closed.connect(handler)

        # DO ACTION
        opp.close_by_deadline()

        # ASSERTS
        self.assertTrue(opp.is_closed)
        self.assertEqual(
            opp.applicants_info.filter_by_status_selected().count(),
            0)
        self.assertEqual(opp.closed_by.user, None)
        self.assertEqual(handler.call_count, 1)
        self.assertIsNone(
            self.get_mock_kwarg(handler, 'comment'),
        )
        self.assertEqual(
            self.get_mock_kwarg(handler, 'origin'),
            settings.OPPORTUNITIES_CH_CLOSE_DEADLINE)
        opportunity_post_closed.disconnect(handler)

    @requests_mock.Mocker()
    def test_signal_close_user_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.handler = mock.Mock()
        opportunity_post_closed.connect(self.handler)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)

        NUM_OTHER_CONSULTANTS = 3
        for _ in range(NUM_OTHER_CONSULTANTS):
            other_user = self.get_user()
            request_mock_account.add_mock(
                other_user, is_consultant=True, is_superuser=False)
            models.Applicant.objects.create_open_applicant(
                other_user, other_user, opp, faker.text())

        # DO ACTION
        opp.close(self.super_user)

        # ASSERTS
        self.assertEqual(
            len(self.get_mock_kwarg(self.handler, 'user_list')),
            NUM_OTHER_CONSULTANTS)
        self.assertEqual(self.handler.call_count, 1)
        opportunity_post_closed.disconnect(self.handler)
