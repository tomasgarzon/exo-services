from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin, request_mock_account

from ..faker_factories.survey import FakeSurveyFactory
from ..faker_factories.survey_filled import FakeSurveyFilledFactory


class SurveyFilledAPITest(UserTestMixin, APITestCase):

    def setUp(self):
        self.create_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_list_survey_filled(self, mock_request):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(
            created_by=self.user)
        FakeSurveyFilledFactory.create_batch(size=3, survey=survey)
        survey_other = FakeSurveyFactory.create(
            created_by=self.get_user())
        FakeSurveyFilledFactory.create_batch(size=3, survey=survey_other)
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        url = reverse('api:survey-filled-list')

        # DO ACTION
        responses = []
        responses.append(self.client.get(url))
        responses.append(self.client.get(url, data={'survey': survey.pk}))

        # ASSERTS
        for response in responses:
            self.assertTrue(status.is_success(response.status_code))
            self.assertEqual(len(response.json()['results']), 3)

    @requests_mock.Mocker()
    def test_retrieve_survey_filled(self, mock_request):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(
            created_by=self.user)
        survey_filled = FakeSurveyFilledFactory.create(survey=survey)
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        url = reverse('api:survey-filled-detail', kwargs={'pk': survey_filled.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_retrieve_survey_filled_download_pdf(self, mock_request):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(
            created_by=self.user)
        survey_filled = FakeSurveyFilledFactory.create(survey=survey)
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        url = reverse('api:filled-download-pdf', kwargs={'pk': survey_filled.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
