import os

from django.test import TestCase

from team.faker_factories import FakeTeamFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin

from ..models import AssignmentStep
from ..conf import settings
from .assignments_mixin import AssignmentsMixin


class AssignmentsPopulatorTest(SuperUserTestMixin, AssignmentsMixin, TestCase):

    def test_assignments_populator_sprint_book(self):
        # PREPARE DATA
        sprint_automated = FakeSprintAutomatedFactory.create()
        team = FakeTeamFactory.create(project=sprint_automated.project_ptr)
        sprint_book_exo_data_path = settings.ASSIGNMENT_EXO_DATA_SPRINT_BOOK_PATH
        sprint_book_num_assignments = len(os.listdir(sprint_book_exo_data_path))

        # DO ACTION
        self.populate_assignments_version_2(
            sprint_automated.project_ptr,
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)

        # ASSERTS
        self.assertEqual(
            AssignmentStep.objects.filter_by_project(sprint_automated.project_ptr).count(),
            sprint_book_num_assignments)

        for step in sprint_automated.steps.all():
            self.assertTrue(step.has_team_assignments(team))
