from django.test import TestCase

from team.faker_factories import FakeTeamFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin

from ..models import AssignmentStep, AssignmentStepTeam
from ..conf import settings
from .assignments_mixin import AssignmentsMixin


class AssignmentStepTeamTest(SuperUserTestMixin, AssignmentsMixin, TestCase):

    def test_assignment_step_teams_creation_after_assignments_content_is_populatated(self):
        # PREPARE DATA
        sprint_automated = FakeSprintAutomatedFactory.create()
        self.populate_assignments_version_2(
            sprint_automated,
            settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK)

        # DO ACTION
        team = FakeTeamFactory.create(project=sprint_automated.project_ptr)

        # ASSERTS
        assignments = AssignmentStep.objects.filter_by_project(
            sprint_automated.project_ptr).filter_by_stream(team.stream)

        for asignment in assignments:
            self.assertTrue(AssignmentStepTeam.objects.filter(
                assignment_step=asignment, team=team).exists())
