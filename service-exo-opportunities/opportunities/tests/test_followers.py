from actstream.models import followers

import requests_mock
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityFollowersTest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def create_initial_scenario(self):
        opp = self.create_opportunity()

        # Create an applicant
        users = []
        for _ in range(2):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            opp.create_open_applicant(
                user, user, summary='')
            users.append(user)

        # Reject
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary='')
        opp.reject(self.super_user, app)

        # Assign
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        app = opp.create_open_applicant(
            user, user, summary="")
        opp.assign(self.super_user, app, '', **self.get_sow_data())

        return opp, users

    @requests_mock.Mocker()
    def test_followers_opp(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp, users = self.create_initial_scenario()
        user1, user2 = users

        # ASSERTS
        opp_followers = followers(opp)

        self.assertEqual(
            len(opp_followers),
            3)

        self.assertTrue(
            user1 in opp_followers)
        self.assertTrue(
            user2 in opp_followers)
