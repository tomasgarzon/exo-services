from django.test import TestCase
from django.conf import settings

import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..faker_factories import FakeOpportunityFactory
from ..models import Opportunity, Applicant


class OpportunityTaggedPITest(
        UserTestMixin,
        OpportunityTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_create_for_tagged_ok(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        users = []
        for _ in range(3):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            users.append(user)
        data = {
            'user_from': self.super_user,
            'users_tagged': users,
            'target': settings.OPPORTUNITIES_CH_TARGET_FIXED,
        }

        # DO ACTION
        opp = FakeOpportunityFactory.create(**data)

        # ASSERTS
        self.assertTrue(opp.is_requested)
        self.assertEqual(opp.users_tagged.count(), 3)
        self.assertTrue(opp.is_tagged)

    def generate_tagged_opportunity(self):
        tagged_user = self.get_user()
        other_user = self.get_user()
        requester_user = self.get_user()
        request_mock_account.add_mock(
            tagged_user, is_consultant=True, is_superuser=False)
        request_mock_account.add_mock(
            other_user, is_consultant=True, is_superuser=False)
        request_mock_account.add_mock(
            requester_user, is_consultant=True, is_superuser=False)
        data = {
            'user_from': requester_user,
            'target': settings.OPPORTUNITIES_CH_TARGET_FIXED,
            'users_tagged': [tagged_user]
        }

        # DO ACTION
        opp = FakeOpportunityFactory.create(**data)
        return tagged_user, other_user, requester_user, opp

    @requests_mock.Mocker()
    def test_tagged_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        tagged_user, other_user, requester_user, _ = self.generate_tagged_opportunity()

        opp_created = Opportunity.objects.filter(
            created_by=requester_user).not_draft()
        opp_other = Opportunity.objects.all_my_opportunities(
            other_user)
        opp_tagged = Opportunity.objects.all_my_opportunities(
            tagged_user)

        # ASSERTS
        self.assertEqual(opp_created.count(), 1)
        self.assertEqual(opp_other.count(), 0)
        self.assertEqual(opp_tagged.count(), 1)

    @requests_mock.Mocker()
    def test_tagged_opp_closed(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        tagged_user, other_user, requester_user, _ = self.generate_tagged_opportunity()
        opp = Opportunity.objects.first()
        applicant = Applicant.objects.create_open_applicant(
            tagged_user, tagged_user, opp, faker.text())
        opp.assign(requester_user, applicant)

        # ASSERTS
        opps_for_tagged_user = Opportunity.objects.all_my_opportunities(tagged_user)
        opps_for_other_user = Opportunity.objects.all_my_opportunities(tagged_user)
        self.assertTrue(
            opps_for_tagged_user.filter(pk=opp.pk).exists())
        self.assertTrue(
            opps_for_other_user.filter(pk=opp.pk).exists())

    @requests_mock.Mocker()
    def test_can_apply(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        tagged_user, other_user, requester_user, opp = self.generate_tagged_opportunity()

        # ASSERTS
        with self.settings(POPULATOR_MODE=False):
            self.assertFalse(opp.can_apply(requester_user, False))
            self.assertFalse(opp.can_apply(other_user, False))
            self.assertTrue(opp.can_apply(tagged_user, False))
            self.assertFalse(
                settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN in opp.user_actions(requester_user))
            self.assertFalse(
                settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN in opp.user_actions(other_user))
            self.assertTrue(
                settings.OPPORTUNITIES_ACTION_CH_APPLY_OPEN in opp.user_actions(tagged_user))
