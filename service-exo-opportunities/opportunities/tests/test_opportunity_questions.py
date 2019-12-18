from django.utils import timezone
from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from exo_role.models import ExORole, CertificationRole

from .. import models
from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account


CERT_COACH = settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH
COACH = settings.EXO_ROLE_CODE_SPRINT_COACH


class QuestionOpportunityAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_create_request_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        keywords = [
            {'name': faker.word() + faker.numerify()},
            {'name': faker.word() + faker.numerify()},
        ]
        data = {
            'title': faker.word(),
            'description': faker.text(),
            'mode': settings.OPPORTUNITIES_CH_MODE_ONSITE,
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'exo_role': ExORole.objects.get(code=COACH).code,
            'certification_required': CertificationRole.objects.get(code=CERT_COACH).code,
            'start_date': timezone.now().date(),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
            'keywords': keywords,
            'entity': faker.company(),
            'budget': 222,
            'budget_currency': settings.OPPORTUNITIES_CH_CURRENCY_EUR,
            'virtual_budget': 222.55,
            'questions': [
                {
                    'title': faker.text(),
                },
                {
                    'title': faker.text(),
                }
            ]
        }
        url = reverse('api:opportunity-list')

        # DO ACTION
        response = self.client.post(url, data=data)
        response_data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opportunity = models.Opportunity.objects.get(
            pk=response_data['pk'])
        self.assertEqual(
            opportunity.questions.count(),
            2
        )
        self.assertTrue(
            models.Question.objects.filter(
                type_question=settings.OPPORTUNITIES_QUESTION_CH_TYPE_DEFAULT
            ).exists()
        )
