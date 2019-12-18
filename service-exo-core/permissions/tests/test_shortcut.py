from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from guardian.shortcuts import assign_perm

from utils.faker_factory import faker
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from customer.tests.test_mixins import TestCustomerMixin
from team.faker_factories import FakeTeamFactory

from ..shortcuts import has_project_perms, has_team_perms


class ShortcutTestCase(
        TestCustomerMixin,
        UserTestMixin,
        SuperUserTestMixin,
        TestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.create_customer()

    def test_sprint_shortcuts(self):
        sprint = self.customer.create_sprint_automated(
            self.super_user,
            faker.first_name(),
            start=timezone.now(),
            description='',
        )
        project = sprint.project_ptr
        team = FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )
        new_user_email = faker.email()
        new_user_name = faker.name()

        member = team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
        )

        FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )
        project.launch(self.super_user, start_date=timezone.now())

        self.assertTrue(
            has_project_perms(project, settings.PROJECT_PERMS_PROJECT_SURVEYS, self.super_user),
        )
        self.assertFalse(
            has_project_perms(project, settings.PROJECT_PERMS_PROJECT_SURVEYS, team.coach.user),
        )
        self.assertFalse(
            has_project_perms(project, settings.PROJECT_PERMS_PROJECT_SURVEYS, member),
        )
        assign_perm(
            settings.PROJECT_PERMS_PROJECT_SURVEYS,
            member, project,
        )
        self.assertTrue(
            has_project_perms(project, settings.PROJECT_PERMS_PROJECT_SURVEYS, member),
        )
        self.assertTrue(
            has_team_perms(team, settings.PROJECT_PERMS_PROJECT_SURVEYS, self.super_user),
        )
