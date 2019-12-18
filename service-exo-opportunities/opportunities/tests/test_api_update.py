from django.utils import timezone
from django.urls import reverse

import requests_mock
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase

from exo_role.models import ExORole, CertificationRole
from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account


CERT_COACH = settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH
COACH = settings.EXO_ROLE_CODE_SPRINT_COACH


class OpportunityUdateAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.add_marketplace_permission(user)
        self.user = user

    @requests_mock.Mocker()
    def test_update_request_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity(user=self.user)
        self.setup_credentials(self.user)
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})
        response = self.client.get(url)
        data = response.json()
        user_tagged = self.get_user()
        request_mock_account.add_mock(
            user_tagged, is_consultant=True, is_superuser=False)
        keywords = [
            {'name': faker.word() + faker.numerify()},
            {'name': faker.word() + faker.numerify()},
        ]
        languages = [
            {'name': faker.word() + faker.numerify()},
        ]
        new_data = {
            'title': faker.word(),
            'description': faker.text(),
            'mode': settings.OPPORTUNITIES_CH_MODE_ONLINE,
            'location_url': faker.uri(),
            'exo_role': ExORole.objects.get(code=COACH).code,
            'certification_required': CertificationRole.objects.get(code=CERT_COACH).code,
            'dueDate': timezone.now().date(),
            'deadline_date': (timezone.now() + timedelta(days=5)).date(),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
            'numPositions': 2,
            'keywords': keywords,
            'languages': languages,
            'entity': faker.company(),
            'target': 'F',
            'users_tagged': [
                {'user': user_tagged.uuid.__str__()},
            ],
            'questions': []
        }
        new_questions = [
            {'id': data.get('questions')[0].get('id'), 'title': faker.word()},
            data.get('questions')[1],
            {'title': faker.word()},
        ]
        data.update(new_data)
        data['budgets'] = [
            {'budget': faker.pyint(), 'currency': settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY_DEFAULT}
        ]
        data.pop('location')
        data['questions'] = new_questions

        # DO ACTION
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})
        response = self.client.put(url, data=data)
        response_data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()

        self.assertIsNotNone(response_data['slug'])
        self.assertEqual(response_data['title'], data['title'])
        self.assertEqual(response_data['description'], data['description'])
        self.assertEqual(response_data['mode'], settings.OPPORTUNITIES_CH_MODE_ONLINE)
        self.assertEqual(opp.keywords.count(), 2)

        budgets = response_data['budgets']
        self.assertIsNone(opp.budget)
        self.assertIsNone(opp.budget_currency)
        self.assertEqual(len(budgets), 1)
        self.assertEqual(budgets[0]['currency'], opp.virtual_budget_currency)
        self.assertEqual(budgets[0]['budget'], opp.virtual_budget.__str__())
        self.assertIsNone(response_data['location'])
        self.assertEqual(
            opp.virtual_budget_currency,
            settings.OPPORTUNITIES_CH_VIRTUAL_CURRENCY_DEFAULT,
        )
        self.assertEqual(response_data['numPositions'], data['numPositions'])
        self.assertEqual(
            len(response_data.get('questions')),
            3)
        for question in new_questions:
            self.assertTrue(opp.questions.filter(title=question['title']).exists())
            if question.get('id'):
                self.assertTrue(opp.questions.filter(pk=question.get('id')).exists())

    @requests_mock.Mocker()
    def test_update_opp_user_tagged(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_USERS = 3
        opp = self.create_opportunity(
            user=self.user, target=settings.OPPORTUNITIES_CH_TARGET_FIXED)
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            opp.users_tagged.create(user=user)
        self.setup_credentials(self.user)
        url = reverse(
            'api:opportunity-admin',
            kwargs={'pk': opp.pk})
        response = self.client.get(url)
        data = response.json()

        keywords = [
            {'name': faker.word() + faker.numerify()},
            {'name': faker.word() + faker.numerify()},
        ]
        new_data = {
            'title': faker.word(),
            'description': faker.text(),
            'mode': settings.OPPORTUNITIES_CH_MODE_ONLINE,
            'location_url': faker.uri(),
            'exo_role': ExORole.objects.get(code=COACH).code,
            'certification_required': CertificationRole.objects.get(code=CERT_COACH).code,
            'dueDate': timezone.now().date(),
            'deadline_date': (timezone.now() + timedelta(days=5)).date(),
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
            'numPositions': 2,
            'keywords': keywords,
            'entity': faker.company(),
            'target': settings.OPPORTUNITIES_CH_TARGET_OPEN,
            'users_tagged': [],
            'questions': []
        }
        data.update(new_data)
        data.pop('location')

        # DO ACTION
        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})
        response = self.client.put(
            url, data=data, **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_opened)
