from django.utils import timezone
from django.urls import reverse

from datetime import timedelta
from unittest import mock

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from exo_role.models import ExORole, CertificationRole
from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from ..conf import settings
from .test_mixin import OpportunityTestMixin, request_mock_account
from ..signals_define import (
    opportunity_deadline,
    opportunity_post_send)


CERT_COACH = settings.EXO_ROLE_CODE_CERTIFICATION_SPRINT_COACH
COACH = settings.EXO_ROLE_CODE_SPRINT_COACH
OTHER_CATEGORY = settings.EXO_ROLE_CATEGORY_OTHER


class OpportunityAPITest(
        UserTestMixin,
        MagicMockMixin,
        OpportunityTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_create_opportunities_permissions(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        super_user = self.super_user
        self.add_marketplace_permission(super_user)
        user_tagged = self.get_user()
        request_mock_account.add_mock(
            user_tagged,
            is_consultant=True,
            is_superuser=False,
        )

        regular_user = self.get_user()
        self.add_marketplace_permission(regular_user)
        request_mock_account.add_mock(
            regular_user,
            is_consultant=True,
            is_superuser=False,
        )

        users_to_create_opp = [
            super_user,
            regular_user,
        ]
        handler = mock.Mock()
        opportunity_deadline.connect(handler)
        for user in users_to_create_opp:
            self.setup_credentials(user)
            data = self.get_api_data(users=[user_tagged])
            url = reverse('api:opportunity-list')

            # DO ACTION
            response = self.client.post(url, data=data)

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))

        self.assertEqual(handler.call_count, 2)
        opportunity_deadline.disconnect(handler)
        for opp in models.Opportunity.objects.all():
            self.assertEqual(opp.users_tagged.count(), 1)
            self.assertTrue(opp.is_tagged)

    @requests_mock.Mocker()
    def test_preview_opportunity_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        TOTAL_USERS = 3
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
        handler = mock.Mock()
        opportunity_deadline.connect(handler)
        opportunity_post_send.connect(handler)
        data = self.get_api_data(users)

        url = reverse('api:opportunity-preview')

        # DO ACTION
        response = self.client.post(url, data=data)
        response_data = response.json()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opportunity = models.Opportunity.objects.get(
            pk=response_data['pk'])
        self.assertTrue(opportunity.is_draft)
        self.assertEqual(response_data.get('userStatus'), settings.OPPORTUNITIES_CH_DRAFT)
        self.assertEqual(response_data['title'], data['title'])
        self.assertIsNotNone(response_data['requestedBy'])
        self.assertEqual(
            len(response_data.get('usersTagged')),
            TOTAL_USERS)
        self.assertEqual(handler.call_count, 0)
        opportunity_deadline.disconnect(handler)
        opportunity_post_send.disconnect(handler)
        self.assertFalse(
            models.Opportunity.objects.filter_for_admin(
            ).filter(pk=opportunity.pk).exists())
        self.assertFalse(
            models.Opportunity.objects.all_my_opportunities(
                self.super_user).filter(pk=opportunity.pk).exists())

    @requests_mock.Mocker()
    def test_opportunity_simple_data_api(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        TOTAL_USERS = 3
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
        keywords = [
            {'name': faker.word() + faker.numerify()},
            {'name': faker.word() + faker.numerify()},
        ]
        data = {
            'title': faker.word(),
            'description': faker.text(),
            'mode': settings.OPPORTUNITIES_CH_MODE_ONSITE,
            'exo_role': ExORole.objects.get(code=COACH).code,
            'certification_required': CertificationRole.objects.get(code=CERT_COACH).code,
            'deadline_date': (timezone.now() + timedelta(days=10)).date(),
            'num_positions': 2,
            'keywords': keywords,
            'target': settings.OPPORTUNITIES_CH_TARGET_FIXED,
            'users_tagged': [
                {'user': user.uuid.__str__()} for user in users
            ],
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
        }
        url = reverse('api:opportunity-preview')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_opportunity_invalid_other_category_data_api(self, mock_request):
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
            'exo_role': ExORole.objects.get(code=COACH).code,
            'other_category_name': faker.word(),
            'certification_required': CertificationRole.objects.get(code=CERT_COACH).code,
            'deadline_date': (timezone.now() + timedelta(days=10)).date(),
            'num_positions': 2,
            'keywords': keywords,
            'target': settings.OPPORTUNITIES_CH_TARGET_OPEN,
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
        }
        url = reverse('api:opportunity-preview')
        # DO ACTION
        response = self.client.post(url, data=data)
        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @requests_mock.Mocker()
    def test_opportunity_other_category_data_api(self, mock_request):
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
            'exo_role': ExORole.objects.get(code=COACH).code,
            'other_category_name': faker.word(),
            'certification_required': OTHER_CATEGORY,
            'deadline_date': (timezone.now() + timedelta(days=10)).date(),
            'num_positions': 2,
            'keywords': keywords,
            'target': settings.OPPORTUNITIES_CH_TARGET_OPEN,
            'duration_unity': settings.OPPORTUNITIES_DURATION_UNITY_DAY,
            'duration_value': 2,
        }
        url = reverse('api:opportunity-preview')
        # DO ACTION
        response = self.client.post(url, data=data)
        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
