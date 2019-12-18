import random
import requests_mock

from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from industry.models import Industry

from ..models import Question
from ..faker_factories.survey import FakeSurveyFactory
from ..faker_factories.survey_filled import FakeSurveyFilledFactory
from ..tasks import SurveyFilledTask


class SurveyAPITest(UserTestMixin, APITestCase):

    def setUp(self):
        self.create_user()

    def test_fill_survey(self):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)
        url = reverse('api:survey-fill', kwargs={'slug': survey.slug})
        data = {
            'name': faker.word(),
            'organization': faker.word(),
            'email': faker.email(),
            'industry': Industry.objects.first().pk,
            'answers': []}
        for question in Question.objects.all():
            option = random.choice(question.options.all())
            data['answers'].append({
                'question': question.pk,
                'option': option.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(survey.surveys_filled.count(), 1)
        self.assertEqual(
            survey.surveys_filled.first().answers.count(),
            Question.objects.all().count())
        self.assertIsNotNone(response.json().get('total'))

    def test_faker_fill_survey(self):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)

        # DO ACTION
        survey_filled = FakeSurveyFilledFactory.create(
            survey=survey)

        # DO ASSERTS
        self.assertEqual(
            survey_filled.answers.count(),
            Question.objects.count())

        self.assertEqual(
            survey_filled.results.count(),
            len(settings.SURVEY_CH_SECTION))

    @requests_mock.Mocker()
    def test_email_task_result(self, mock):
        # PREPARE DATA
        survey = FakeSurveyFactory.create(created_by=self.user)
        mock.post(
            '{}{}{}'.format(
                settings.EXOLEVER_HOST,
                settings.SERVICE_EXO_MAIL_HOST,
                'api/mail/'),
            json={})
        survey_filled = FakeSurveyFilledFactory.create(
            survey=survey)

        # DO ACTION
        SurveyFilledTask().s(pk=survey_filled.pk).apply()

        # DO ASSERTS
        self.assertTrue(mock.called)
        request = mock.request_history[0]
        mandatory_values = [
            'params', 'template', 'domain'
        ]
        params_values = [
            'name', 'survey_name', 'organization', 'public_url', 'total'
        ]
        request_data = request.json()
        for value in mandatory_values:
            self.assertIsNotNone(request_data.get(value), value)
        for value in params_values:
            self.assertIsNotNone(eval(request_data['params']).get(value), value)
