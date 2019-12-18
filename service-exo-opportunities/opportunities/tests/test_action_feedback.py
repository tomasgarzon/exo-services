from django.test import TestCase

import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityActionFeedbackTest(
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

    def get_feedback(self):
        return {
            'comment': faker.text(),
            'explained': 1,
            'collaboration': 2,
            'communication': 3,
            'recommendation': 4,
        }

    @requests_mock.Mocker()
    def test_requester_give_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        applicant.set_completed()

        # DO ACTION
        applicant.give_feedback(self.super_user, **self.get_feedback())

        # ASSERTS
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_feedback_requester_received)
        self.assertEqual(applicant.feedbacks.all().count(), 1)
        self.assertEqual(applicant.feedbacks.filter(created_by=opp.created_by).count(), 1)

    @requests_mock.Mocker()
    def test_applicant_give_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        applicant.set_completed()

        # DO ACTION
        applicant.give_feedback(user, **self.get_feedback())

        # ASSERTS
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_feedback_applicant_received)
        self.assertEqual(applicant.feedbacks.all().count(), 1)
        self.assertEqual(applicant.feedbacks.filter(created_by=user).count(), 1)

    @requests_mock.Mocker()
    def test_both_give_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        applicant.set_completed()

        # DO ACTION
        applicant.give_feedback(user, **self.get_feedback())
        applicant.give_feedback(opp.created_by, **self.get_feedback())

        # ASSERTS
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_feedback_received)
        self.assertEqual(applicant.feedbacks.all().count(), 2)
        self.assertEqual(applicant.feedbacks.filter(created_by=user).count(), 1)
        self.assertEqual(applicant.feedbacks.filter(created_by=opp.created_by).count(), 1)
