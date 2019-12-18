from django.test import TestCase
from django.conf import settings

from utils.test_mixin import UserTestMixin
from utils.permissions.objects_project import get_project_for_user

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class ProjectPermissionsTest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def test_user_roles(self):
        # PREPARE DATA
        admin = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        basic = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        readonly = self.project.project_roles.get(code='SOB')
        notification = self.project.project_roles.get(code='SAM')

        # DO ACTION
        user_admin_and_basic = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=admin,
            user=user_admin_and_basic)
        models.UserProjectRole.objects.create(
            project_role=basic,
            user=user_admin_and_basic)

        user_basic = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=basic,
            user=user_basic)

        user_readonly = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=readonly,
            user=user_readonly)

        user_basic_and_notification = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=notification,
            user=user_basic_and_notification)
        models.UserProjectRole.objects.create(
            project_role=basic,
            user=user_basic_and_notification)

        for user_project_role in models.UserProjectRole.objects.filter(project_role__project=self.project):
            user_project_role.activate(self.super_user)

        #  ASSERTS
        self.assertTrue(self.project.user_is_admin(user_admin_and_basic))
        self.assertTrue(self.project.user_is_basic(user_admin_and_basic))

        self.assertTrue(self.project.user_is_basic(user_basic))

        self.assertTrue(
            self.project.user_is_readonly(user_readonly))

        self.assertTrue(
            self.project.user_is_basic(user_basic_and_notification))
        self.assertTrue(
            self.project.user_is_notification(user_basic_and_notification))
        users = [user_admin_and_basic, user_basic, user_readonly, user_basic_and_notification]
        for user in users:
            self.assertEqual(
                list(get_project_for_user(user)),
                [self.project])

    def test_user_roles_remove(self):
        # PREPARE DATA
        admin = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        basic = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        # DO ACTION
        user = self.get_user()
        user_project_role = models.UserProjectRole.objects.create(
            project_role=admin,
            user=user,
            active=True)
        models.UserProjectRole.objects.create(
            project_role=basic,
            user=user,
            active=True)

        user_project_role.delete()

        #  ASSERTS
        self.assertFalse(self.project.user_is_admin(user))
        self.assertTrue(self.project.user_is_basic(user))
