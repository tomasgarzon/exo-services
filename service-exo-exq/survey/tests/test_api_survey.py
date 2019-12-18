from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin, request_mock_account

from ..models import Survey
from ..faker_factories.survey import FakeSurveyFactory


class SurveyAPITest(UserTestMixin, APITestCase):

    def setUp(self):
        self.create_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_create_survey(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        url = reverse('api:survey-list')
        data = {
            'name': faker.word(),
            'slug': faker.word(),
            'send_results': True,
            'language': settings.SURVEY_CH_SPANISH,
            'show_results': True}

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Survey.objects.filter(created_by=self.user, name=data['name']).count(), 1)
        self.assertEqual(
            Survey.objects.filter(created_by=self.user, name=data['name']).first().language,
            settings.SURVEY_CH_SPANISH)

    @requests_mock.Mocker()
    def test_create_multiple_survey(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        data = {
            'name': faker.word(),
            'slug': faker.word(),
            'send_results': True,
            'show_results': True}
        url = reverse('api:survey-list')

        # DO ACTION
        TOTAL_SURVEYS = 20
        for _ in range(TOTAL_SURVEYS):
            data['name'] = faker.word() + ' ' + faker.numerify()
            data['slug'] = data['name'].replace(' ', '-')
            response = self.client.post(url, data=data)

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))

        response = self.client.get(url)
        self.assertEqual(response.json()['count'], TOTAL_SURVEYS)
        self.assertEqual(len(response.json()['results']), 10)
        self.assertEqual(
            Survey.objects.filter(
                created_by=self.user).count(), TOTAL_SURVEYS)

    @requests_mock.Mocker()
    def test_update_survey(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        survey = FakeSurveyFactory.create(created_by=self.user)
        url = reverse('api:survey-detail', kwargs={'pk': survey.pk})
        data = {
            'name': faker.word(),
            'slug': faker.word(),
            'send_results': False,
            'show_results': False}

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            Survey.objects.filter(created_by=self.user, name=data['name']).count(), 1)

    @requests_mock.Mocker()
    def test_get_survey(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        user = self.get_user()
        data = {
            'name': faker.word(),
            'slug': faker.word(),
            'send_results': True,
            'show_results': True}
        url = reverse('api:survey-list')

        # DO ACTION
        for _ in range(3):
            data['name'] = faker.word()
            data['slug'] = data['name']
            response = self.client.post(url, data=data)
        self.setup_credentials(user)
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'],
            0)

    @requests_mock.Mocker()
    def test_get_survey_xlsx_report(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        survey = FakeSurveyFactory.create(created_by=self.user)
        url = reverse('api:survey-download-csv', kwargs={'pk': survey.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(type(response.content).__name__, 'bytes')

    @requests_mock.Mocker()
    def test_survey_check_slug(self, mock_request):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(
            created_by=self.user)
        url = reverse('api:check-slug')

        # DO ACTION
        response = self.client.get(url, data={'slug': survey.slug})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data)

        # DO ACTION
        response = self.client.get(url, data={'slug': faker.word()})

        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(response.data)
