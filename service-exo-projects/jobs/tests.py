from django.test import TestCase

from project.faker_factories import (
    FakeProjectFactory,
    FakeUserProjectFactory,
)
from utils.test_mixin import UserTestMixin


class JobsTestCase(UserTestMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.create_user()
        self.project = FakeProjectFactory.create(created_by=self.user)

    def test_job_for_user_project_roles_active(self):
        # PREPARE DATA
        project_role = self.project.project_roles.first()

        # DO ACTION
        user_project_role = FakeUserProjectFactory.create(
            user=self.user,
            project_role=project_role,
            active=True)

        # ASSERTS
        self.assertIsNotNone(user_project_role.job)

    def test_job_for_user_project_roles_inactive(self):
        # PREPARE DATA
        project_role = self.project.project_roles.first()

        # DO ACTION
        user_project_role = FakeUserProjectFactory.create(
            user=self.user,
            project_role=project_role,
            active=False)

        # ASSERTS
        self.assertFalse(hasattr(user_project_role, 'job'))
