from django.test import TestCase

import requests_mock
from unittest import mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account

from ..signals_define import opportunity_post_edited


class OpportunityActionRequesterTest(
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

    @requests_mock.Mocker()
    def test_notification_signal_for_editing(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.handler = mock.Mock()
        opportunity_post_edited.connect(self.handler)
        opp = self.create_opportunity()
        comment = faker.text()

        # DO ACTION
        models.Opportunity.objects.update_opportunity(
            user_from=opp.created_by,
            opportunity=opp,
            keywords=[],
            questions=[],
            comment=comment,
            target=opp.target,
            send_notification=True)

        # ASSERTS
        self.assertEqual(
            self.get_mock_kwarg(self.handler, 'comment'),
            comment)
        self.assertEqual(self.handler.call_count, 1)
        opportunity_post_edited.disconnect(self.handler)
