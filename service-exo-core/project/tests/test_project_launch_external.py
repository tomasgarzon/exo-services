from django.test import TestCase
from django.conf import settings
from unittest.mock import patch

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from customer.tests.test_mixins import TestCustomerMixin
from team.faker_factories import FakeTeamFactory
from exo_accounts.test_mixins import FakeUserFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from opportunities.signals.opportunity import project_launch_handler


class ProjectLaunchExternalTestCase(
        TestCustomerMixin,
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.create_customer()

    def create_sprint(self):
        self.secondary_user = FakeUserFactory.create()
        self.sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        self.team_A = FakeTeamFactory.create(
            project=self.sprint.project_ptr)
        self.team_B = FakeTeamFactory.create(
            project=self.sprint.project_ptr)

        self.team_A.add_member(
            user_from=self.super_user,
            email=self.user.email,
            name=self.user.short_name)

        self.team_B.add_member(
            user_from=self.super_user,
            email=self.secondary_user.email,
            name=self.secondary_user.short_name)

    @patch('project.tasks.project_conversations.CreateConversationProjectTask.apply_async')
    def test_sprint_launch(self, mock_task_chat):
        #  PREPARE DATA
        self.create_sprint()
        project = self.sprint.project_ptr

        # DO ACTION
        project.launch(self.super_user)

        # ASSERT
        self.assertTrue(mock_task_chat.called)

    def test_create_opportunity_groups(self):
        # PREPARE DATA
        self.create_sprint()
        project = self.sprint.project_ptr

        # DO ACTION
        project_launch_handler(project.__class__, project)

        # ASSERTS
        self.assertIsNotNone(project.advisor_request_settings)
        for team in project.teams.all():
            self.assertIsNotNone(team.opportunity_group)
