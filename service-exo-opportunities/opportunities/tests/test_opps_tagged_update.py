from django.test import TestCase
from django.conf import settings

import requests_mock
from unittest import mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..models import Opportunity, Applicant
from ..signals_define import (
    opportunity_post_rejected, opportunity_post_send,
    opportunity_send_to_user)


class OpportunityTaggedUpdateAPITest(
        UserTestMixin,
        MagicMockMixin,
        OpportunityTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def create_applicant(self, opp, user=None):
        if user is None:
            applicant_user = self.get_user()
        else:
            applicant_user = user
        request_mock_account.add_mock(
            applicant_user, is_consultant=True, is_superuser=False)
        return Applicant.objects.create_open_applicant(
            applicant_user, applicant_user, opp, faker.text())

    @requests_mock.Mocker()
    def test_open_to_target(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_USERS = 3
        opp = self.create_opportunity()
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)

        self.create_applicant(opp)
        self.create_applicant(opp, users[0])

        self.handler = mock.Mock()
        opportunity_post_rejected.connect(self.handler)
        self.handler2 = mock.Mock()
        opportunity_post_send.connect(self.handler2)

        # DO ACTION
        Opportunity.objects.update_opportunity(
            user_from=opp.created_by,
            opportunity=opp,
            keywords=[],
            questions=[],
            target=settings.OPPORTUNITIES_CH_TARGET_FIXED,
            users_tagged=[user.uuid for user in users],
            send_notification=True)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_tagged)
        self.assertEqual(opp.applicants_info.count(), 1)
        self.assertEqual(opp.users_tagged.count(), TOTAL_USERS)
        self.assertTrue(opp.applicants_info.filter(user=users[0]).exists())
        self.assertEqual(self.handler.call_count, 1)
        self.assertEqual(self.handler2.call_count, 0)
        opportunity_post_rejected.disconnect(self.handler)
        opportunity_post_send.disconnect(self.handler2)

    @requests_mock.Mocker()
    def test_target_to_open(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_USERS = 3
        opp = self.create_opportunity(target=settings.OPPORTUNITIES_CH_TARGET_FIXED)
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            opp.users_tagged.create(user=user)

        self.create_applicant(opp, users[0])

        self.handler = mock.Mock()
        opportunity_post_send.connect(self.handler)

        # DO ACTION
        Opportunity.objects.update_opportunity(
            user_from=opp.created_by,
            opportunity=opp,
            keywords=[],
            questions=[],
            target=settings.OPPORTUNITIES_CH_TARGET_OPEN,
            users_tagged=[],
            send_notification=True)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_opened)
        self.assertEqual(opp.applicants_info.count(), 1)
        self.assertEqual(opp.users_tagged.count(), 0)
        self.assertTrue(opp.applicants_info.filter(user=users[0]).exists())
        self.assertEqual(self.handler.call_count, 1)
        self.assertIsNone(
            self.get_mock_kwarg(self.handler, 'user'))
        opportunity_post_send.disconnect(self.handler)

    @requests_mock.Mocker()
    def test_target_to_target(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_INITIAL_USERS = 3
        TOTAL_EDITED_USERS = 4
        TOTAL_USERS = 5
        opp = self.create_opportunity(target=settings.OPPORTUNITIES_CH_TARGET_FIXED)
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)

        initial_users = users[:TOTAL_INITIAL_USERS]
        for user in initial_users:
            opp.users_tagged.create(user=user)
            self.create_applicant(opp, user)

        self.handler_send = mock.Mock()
        self.handler_rejected = mock.Mock()
        opportunity_send_to_user.connect(self.handler_send)
        opportunity_post_rejected.connect(self.handler_rejected)

        # DO ACTION
        edited_users = users[1:]

        Opportunity.objects.update_opportunity(
            user_from=opp.created_by,
            opportunity=opp,
            keywords=[],
            questions=[],
            target=settings.OPPORTUNITIES_CH_TARGET_FIXED,
            users_tagged=[user.uuid for user in edited_users],
            send_notification=True)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(opp.is_tagged)
        self.assertEqual(opp.applicants_info.count(), 2)
        self.assertEqual(opp.users_tagged.count(), TOTAL_EDITED_USERS)
        self.assertEqual(self.handler_send.call_count, 2)
        self.assertTrue(
            self.get_mock_kwarg(self.handler_send, 'user') in users[3:]
        )
        self.assertEqual(self.handler_rejected.call_count, 1)
        opportunity_send_to_user.disconnect(self.handler_send)
        opportunity_post_rejected.disconnect(self.handler_rejected)
