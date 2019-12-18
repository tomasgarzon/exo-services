from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase
from exo_role.models import ExORole
from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..conf import settings

from .test_mixin import OpportunityTestMixin, request_mock_account


class OpportunityBadgeAPITest(
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
    def test_api_badges(self, mock_request):
        # PREPARE DATA
        EXO_ROLES = [
            settings.EXO_ROLE_CODE_ADVISOR,
            settings.EXO_ROLE_CODE_FASTRACK_TEAM_MEMBER,
            settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
            settings.EXO_ROLE_CODE_SPRINT_REPORTER,
        ]
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        users = []
        for code in EXO_ROLES:
            exo_role = ExORole.objects.get(code=code)
            opp = self.create_opportunity(user=user, role=exo_role)
            other_user = self.get_user()
            request_mock_account.add_mock(
                other_user, is_consultant=True, is_superuser=False)
            applicant = models.Applicant.objects.create_open_applicant(
                other_user, other_user, opp, faker.text())
            opp.assign(user, applicant)
            users.append(other_user)

        # DO ACTION
        url = reverse('api:opportunity-badges-list')
        self.setup_username_credentials()
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(len(data), len(EXO_ROLES))
