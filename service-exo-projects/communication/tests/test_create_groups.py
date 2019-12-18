from django.conf import settings
from django.test import TestCase

import requests_mock

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from project import models
from project.faker_factories import FakeProjectFactory
from project.tests.test_mixin import ProjectTestMixin, request_mock_account
from team.faker_factories import FakeTeamFactory

from ..helper import initialize_groups_for_project


class CreateGroupAPITest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)
        cls.init_project(cls)

    def init_project(cls):
        head_coach_role = cls.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        coach_role = cls.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user_hc = cls.get_user(cls)
        request_mock_account.add_mock(
            user_hc, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=head_coach_role,
            user=user_hc)
        user_coach = cls.get_user(cls)
        request_mock_account.add_mock(
            user_coach, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            teams=cls.project.teams.all(),
            user=user_coach)
        users_participants = []
        for team in cls.project.teams.all():
            user_role = models.UserProjectRole.objects.create_participant(
                project=cls.project,
                teams=[team],
                name=faker.name(),
                email=faker.email())
            request_mock_account.add_mock(
                user_role.user, is_consultant=False, is_superuser=False)
            users_participants.append(user_role.user)
        cls.user_coach = user_coach
        cls.user_hc = user_hc
        cls.users_participants = users_participants

    @requests_mock.Mocker()
    def test_create_groups(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_GROUPS = 6

        # DO ACTION
        initialize_groups_for_project(self.project, self.project.created_by)

        # ASSERTS
        self.assertEqual(
            self.project.groups.count(),
            TOTAL_GROUPS)
        self.assertEqual(
            self.user_hc.communication_groups.count(), TOTAL_GROUPS)
        self.assertEqual(
            self.user_coach.communication_groups.count(), TOTAL_GROUPS)
        for user in self.users_participants:
            self.assertEqual(
                user.communication_groups.count(), 2)
        for team in self.project.teams.all():
            self.assertIsNotNone(team.group)

    @requests_mock.Mocker()
    def test_create_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_GROUPS = 7
        initialize_groups_for_project(self.project, self.project.created_by)

        # DO ACTION
        team = FakeTeamFactory.create(
            project=self.project,
            created_by=self.project.created_by)

        # ASSERTS
        self.assertEqual(
            self.project.groups.count(),
            TOTAL_GROUPS)
        self.assertEqual(
            self.user_hc.communication_groups.count(), TOTAL_GROUPS)
        for team in self.project.teams.all():
            self.assertIsNotNone(team.group)

    @requests_mock.Mocker()
    def test_delete_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_GROUPS = 5
        initialize_groups_for_project(self.project, self.project.created_by)

        # DO ACTION
        team = self.project.teams.first()
        team.delete()

        # ASSERTS
        self.assertEqual(
            self.project.groups.count(),
            TOTAL_GROUPS)

    @requests_mock.Mocker()
    def test_adding_users(self, mock_request):
        # PREPARE DATA
        TOTAL_GROUPS = 6
        TOTAL_USERS = 8
        TOTAL_COLLABORATORS = 4
        self.init_mock(mock_request)
        initialize_groups_for_project(self.project, self.project.created_by)
        head_coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        # DO ACTION
        user_hc = self.get_user()
        request_mock_account.add_mock(
            user_hc, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=head_coach_role,
            user=user_hc)
        user_coach = self.get_user()
        request_mock_account.add_mock(
            user_coach, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            teams=self.project.teams.all(),
            user=user_coach)

        # ASSERTS
        self.assertEqual(
            self.project.groups.count(),
            TOTAL_GROUPS)
        self.assertEqual(
            self.project.groups.get(
                group_type=settings.COMMUNICATION_CH_GENERAL).users.count(),
            TOTAL_USERS)
        self.assertEqual(
            self.project.groups.get(
                group_type=settings.COMMUNICATION_CH_COLLABORATORS).users.count(),
            TOTAL_COLLABORATORS)
        for team in self.project.teams.all():
            self.assertEqual(team.group.users.count(), 5)
