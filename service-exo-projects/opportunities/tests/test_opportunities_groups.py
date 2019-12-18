from django.test import TestCase

import requests_mock

from utils.test_mixin import UserTestMixin
from project.faker_factories import FakeProjectFactory
from project.tests.test_mixin import ProjectTestMixin
from team.faker_factories import FakeTeamFactory

from ..models import OpportunityTeamGroup
from ..signals.opportunity import project_launch_handler


class OpportunitiesGroupAPITest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    @requests_mock.Mocker()
    def test_create_groups(self, mock_request):
        # DO ACTION
        self.project.refresh_from_db()
        project_launch_handler(self.project.__class__, self.project)

        # ASSERTS
        self.assertIsNotNone(self.project.advisor_request_settings)
        for team in self.project.teams.all():
            self.assertIsNotNone(team.opportunity_group)

    @requests_mock.Mocker()
    def test_create_team(self, mock_request):
        # PREPARE DATA
        self.project.refresh_from_db()
        self.project.sync_launch(self.super_user)
        project_launch_handler(self.project.__class__, self.project)
        TOTAL_GROUPS = 5

        # DO ACTION
        FakeTeamFactory.create(
            project=self.project,
            created_by=self.project.created_by)

        # ASSERTS
        self.assertEqual(
            OpportunityTeamGroup.objects.filter(team__project=self.project).count(),
            TOTAL_GROUPS)

    @requests_mock.Mocker()
    def test_delete_team(self, mock_request):
        # PREPARE DATA
        self.project.refresh_from_db()
        project_launch_handler(self.project.__class__, self.project)
        TOTAL_GROUPS = 3

        # DO ACTION
        team = self.project.teams.first()
        team.delete()

        # ASSERTS
        self.assertEqual(
            OpportunityTeamGroup.objects.filter(team__project=self.project).count(),
            TOTAL_GROUPS)
