import uuid

from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin

from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account
from ..models import UserProjectRole


class OpportunityProjectTest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.create_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)
        request_mock_account.add_mock(
            self.user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_project_detail(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        url = reverse('api:project-opportunities-add-from-opportunity', kwargs={'uuid': self.project.uuid.__str__()})
        self.setup_username_credentials()
        data = {
            'user': self.user.uuid.__str__(),
            'user_from': self.super_user.uuid.__str__(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_COACH,
            'opportunity_uuid': uuid.uuid4().__str__()
        }

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        user_project_role = UserProjectRole.objects.filter(
            project_role__project=self.project,
            user__uuid=data['user']).first()
        self.assertIsNotNone(user_project_role)
        self.assertEqual(
            user_project_role.project_role.exo_role.code,
            data['exo_role'])
        self.assertEqual(
            user_project_role.opportunity_related.opportunity_uuid.__str__(),
            data['opportunity_uuid'])
