from django.urls import reverse
from django.conf import settings

import requests_mock

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


TOTAL_ROLES_FOR_SPRINT = 14


class RoleProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def get_data(self):
        return {
            'order': faker.pyint(),
            'level': settings.PROJECT_CH_ROLE_LEVEL_ADMIN,
            'default': True,
            'role': 'Advisor',
            'code': settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER,
            'exoRole': settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER
        }

    @requests_mock.Mocker()
    def test_role_list(self, mock_request):
        url = reverse('api:project-role-list', kwargs={'project_pk': self.project.pk})

        # ASSERTS
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.json()), TOTAL_ROLES_FOR_SPRINT)

    @requests_mock.Mocker()
    def test_create_role(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        data = self.get_data()
        url = reverse('api:project-role-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.project_roles.count(),
            TOTAL_ROLES_FOR_SPRINT + 1)

    @requests_mock.Mocker()
    def test_role_edit(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        role = self.project.project_roles.get(
            code=settings.EXO_ROLE_CODE_ADVISOR)
        url = reverse(
            'api:project-role-detail',
            kwargs={
                'pk': role.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        data = self.get_data()
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        role.refresh_from_db()
        self.assertEqual(role.role, data['role'])
        self.assertEqual(self.project.project_roles.count(), TOTAL_ROLES_FOR_SPRINT)

    @requests_mock.Mocker()
    def test_role_delete(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        role = self.project.project_roles.first()
        url = reverse(
            'api:project-role-detail',
            kwargs={
                'pk': role.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        with self.assertRaises(models.ProjectRole.DoesNotExist):
            role.refresh_from_db()
        self.assertEqual(
            self.project.project_roles.count(), TOTAL_ROLES_FOR_SPRINT - 1)
