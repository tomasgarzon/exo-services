from django.conf import settings
from django.urls import reverse
from django.test import TestCase

from rest_framework import status

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from generic_project.faker_factories import GenericProjectFactory
from utils.faker_factory import faker
from consultant.faker_factories import FakeConsultantFactory
from team.models import Team


class CertificationProjectTestCase(
        SuperUserTestMixin,
        UserTestMixin,
        TestCase):

    def setUp(self):
        self.create_user()
        self.create_superuser()
        FakeConsultantFactory.create(
            user=self.user,
        )
        manager = FakeConsultantFactory.create(
            user=self.super_user,
        )
        generic_project = GenericProjectFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_DRAFT,
            created_by=self.super_user)
        generic_project.launch(self.super_user)
        Team.objects.create(
            project=generic_project.project_ptr,
            user_from=self.super_user,
            created_by=self.super_user,
            name=faker.name(),
            coach=manager,
            stream=settings.PROJECT_STREAM_CH_STRATEGY,
            team_members=[],
        )
        self.project = generic_project.project_ptr

    def test_create_ok_default_language(self):
        project_id = self.project.id
        url = reverse('certification:level-1')
        self.client.login(username=self.user.username, password='123456')

        with self.settings(
                EXO_FOUNDATIONS_EN=project_id,
                PROJECT_CERTIFICATION_LEVEL_1=[project_id, ],
                PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE={'en': project_id}):
            response = self.client.post(url)
            self.assertTrue(status.is_redirect(response.status_code))
            self.assertTrue(self.project.has_perm(self.user, settings.PROJECT_PERMS_VIEW_PROJECT))
            self.assertEqual(
                response.url,
                settings.DOMAIN_NAME + self.project.get_frontend_index_url(self.user))

    def test_create_fail_default_language(self):
        project_id = self.project.id
        url = reverse('certification:level-1')
        self.client.login(username=self.user.username, password='123456')

        with self.settings(
                EXO_FOUNDATIONS_EN=project_id,
                PROJECT_CERTIFICATION_LEVEL_1=[project_id, ],
                PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE={'es': project_id}):
            response = self.client.post(url)
            self.assertTrue(status.is_redirect(response.status_code))
            self.assertFalse(self.project.has_perm(self.user, settings.PROJECT_PERMS_VIEW_PROJECT))
            self.assertIsNone(self.project.get_frontend_index_url(self.user))

    def test_create_ok(self):
        project_id = self.project.id
        url = reverse('certification:level-1', kwargs={'language': 'en'})
        self.client.login(username=self.user.username, password='123456')

        with self.settings(
                EXO_FOUNDATIONS_EN=project_id,
                PROJECT_CERTIFICATION_LEVEL_1=[project_id, ],
                PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE={'en': project_id}):
            response = self.client.post(url)
            self.assertTrue(status.is_redirect(response.status_code))
            self.assertTrue(self.project.has_perm(self.user, settings.PROJECT_PERMS_VIEW_PROJECT))
            self.assertEqual(
                response.url,
                settings.DOMAIN_NAME + self.project.get_frontend_index_url(self.user))

    def test_create_ok_for_spanish_language(self):
        project_id = self.project.id
        url = reverse('certification:level-1', kwargs={'language': 'es'})
        self.client.login(username=self.user.username, password='123456')

        with self.settings(
                EXO_FOUNDATIONS_ES=project_id,
                PROJECT_CERTIFICATION_LEVEL_1=[project_id, ],
                PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE={'es': project_id}):
            response = self.client.post(url)
            self.assertTrue(status.is_redirect(response.status_code))
            self.assertTrue(self.project.has_perm(self.user, settings.PROJECT_PERMS_VIEW_PROJECT))
            self.assertEqual(
                response.url,
                settings.DOMAIN_NAME + self.project.get_frontend_index_url(self.user),
            )

    def test_create_ko(self):
        url = reverse('certification:level-1', kwargs={'language': 'en'})
        self.client.login(username=self.user.username, password='123456')

        response = self.client.post(url)
        self.assertTrue(status.is_redirect(response.status_code))

        self.assertFalse(self.project.has_perm(self.user, settings.PROJECT_PERMS_VIEW_PROJECT))
        self.assertEqual(response.url, settings.DOMAIN_NAME)

    def test_create_twice(self):
        project_id = self.project.id
        url = reverse('certification:level-1', kwargs={'language': 'en'})
        self.client.login(username=self.user.username, password='123456')

        with self.settings(
                EXO_FOUNDATIONS_EN=project_id,
                PROJECT_CERTIFICATION_LEVEL_1=[project_id, ],
                PROJECT_CERTIFICATION_LEVEL_1_LANGUAGE={'en': project_id}):
            response = self.client.post(url)
            response_duplicated = self.client.post(url)
            self.assertTrue(status.is_redirect(response.status_code))
            self.assertTrue(status.is_redirect(response_duplicated.status_code))
            self.assertTrue(self.project.has_perm(self.user, settings.PROJECT_PERMS_VIEW_PROJECT))
            self.assertEqual(
                response.url,
                settings.DOMAIN_NAME + self.project.get_frontend_index_url(self.user),
            )
