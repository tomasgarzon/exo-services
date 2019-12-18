from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityFeedbackAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

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
    def test_feedback_requester_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        applicant.set_completed()
        self.setup_credentials(self.super_user)

        url = reverse(
            'api:applicant-give-feedback',
            kwargs={'pk': applicant.pk})
        data = self.get_feedback()
        data['status'] = settings.OPPORTUNITIES_JOB_DONE

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_feedback_requester_received)
        feedback = applicant.feedbacks.first()
        self.assertEqual(feedback.created_by, self.super_user)
        self.assertEqual(len(response.json()['applicants']), 1)

    @requests_mock.Mocker()
    def test_feedback_applicant_api(self, mock_request):
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
        self.setup_credentials(user)

        url = reverse(
            'api:applicant-give-feedback',
            kwargs={'pk': applicant.pk})
        data = self.get_feedback()

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_feedback_applicant_received)
        feedback = applicant.feedbacks.first()
        self.assertEqual(feedback.created_by, user)

    @requests_mock.Mocker()
    def test_feedback_requester_after_applicant_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user_creator = self.get_user()
        request_mock_account.add_mock(
            user_creator, is_consultant=False, is_superuser=True)
        opp = self.create_opportunity(user_creator)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(user_creator, applicant)
        applicant.set_completed()
        applicant.give_feedback(user, **self.get_feedback())
        self.setup_credentials(user_creator)

        url = reverse(
            'api:applicant-give-feedback',
            kwargs={'pk': applicant.pk})
        data = self.get_feedback()
        data['status'] = settings.OPPORTUNITIES_JOB_DONE

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        applicant.refresh_from_db()
        self.assertTrue(applicant.is_feedback_received)

    @requests_mock.Mocker()
    def test_applicant_feedbacks(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.add_marketplace_permission(user)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        applicant.set_completed()
        applicant.give_feedback(user, **self.get_feedback())
        applicant.give_feedback(opp.created_by, **self.get_feedback())

        # DO ACTION FOR APPLICANT
        self.setup_credentials(user)
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})

        response = self.client.get(url)

        # ASSERTS
        response_data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response_data.get('myApplicant').get('feedbacks')),
            2)

        # DO ACTION FOR REQUESTER
        self.setup_credentials(opp.created_by)
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})

        response = self.client.get(url)

        # ASSERTS
        response_data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response_data.get('applicants')[0].get('feedbacks')),
            2)
