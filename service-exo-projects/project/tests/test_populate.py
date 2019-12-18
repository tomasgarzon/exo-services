from django.test import TestCase

# from utils.faker_factories import FakeUserFactory
from assignment.models import AssignmentStep
from team.faker_factories import FakeTeamFactory

from utils.test_mixin import UserTestMixin

from ..faker_factories import FakeProjectFactory
from ..conf import settings


class ProjectPopulateFakerTest(UserTestMixin, TestCase):

    def test_populate_project_automated(self):
        # DATA
        self.create_user()
        created_by = self.user
        # DO ACTION
        project = FakeProjectFactory.create(
            content_template=settings.PROJECT_CH_PROJECT_TEMPLATE_AUTOMATED,
            created_by=created_by)
        team = FakeTeamFactory.create(
            project=project,
            created_by=project.created_by)

        # ASSERTS
        self.assertTrue(project.settings)
        self.assertFalse(project.settings.ask_to_ecosystem)
        self.assertTrue(project.settings.launch['send_welcome_consultant'])
        self.assertTrue(project.settings.launch['send_welcome_participant'])
        self.assertFalse(project.settings.team_communication)

        self.assertTrue(project.steps.exists())
        self.assertTrue(project.project_roles.exists())
        self.assertTrue(project.team_roles.exists())
        self.assertTrue(project.teams.exists())

        self.assertEqual(project.steps.count(), 13)
        self.assertEqual(project.project_roles.count(), 14)
        self.assertEqual(project.team_roles.count(), 2)
        self.assertEqual(project.teams.count(), 5)

        self.assertEqual(AssignmentStep.objects.filter_by_project(
            project).count(), 23)

        for step in project.steps.all():
            self.assertTrue(AssignmentStep.objects.filter_by_step(step).exists())

        for assignment in AssignmentStep.objects.filter_by_project(
                project).filter_by_stream(team.stream):
            self.assertTrue(team.assignment_step_teams.filter(assignment_step=assignment).exists())

    def test_populate_project_fastrack(self):
        # DO ACTION
        project = FakeProjectFactory.create(
            content_template=settings.PROJECT_CH_PROJECT_TEMPLATE_FASTRACK,
            created_by=self.create_user())

        # ASSERTS
        self.assertFalse(project.steps.exists())
        self.assertTrue(project.project_roles.exists())
        self.assertTrue(project.team_roles.exists())
        self.assertEqual(project.project_roles.count(), 8)
        self.assertEqual(project.team_roles.count(), 2)

    def test_populate_project_blank(self):
        # DO ACTION
        project = FakeProjectFactory.create(
            content_template=settings.PROJECT_CH_PROJECT_TEMPLATE_BLANK,
            created_by=self.create_user())

        # ASSERTS
        self.assertTrue(project.settings)
        self.assertFalse(project.steps.exists())
        self.assertTrue(project.project_roles.exists())
        self.assertTrue(project.team_roles.exists())
        self.assertEqual(project.project_roles.count(), 1)
        self.assertEqual(project.team_roles.count(), 2)
