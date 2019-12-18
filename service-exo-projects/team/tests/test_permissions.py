from django.test import TestCase
from django.conf import settings

from utils.test_mixin import UserTestMixin
from utils.permissions.objects_project import get_project_for_user
from utils.permissions.objects import get_team_for_user
from project.faker_factories import FakeProjectFactory
from project.tests.test_mixin import ProjectTestMixin, request_mock_account
from project.models import UserProjectRole


class TeamPermissionsTest(
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
        project_coach = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        project_participant = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        head_coach = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)

        # DO ACTION
        coaches_users = []
        for team in self.project.teams.all():
            user_coach = self.get_user()
            UserProjectRole.objects.create(
                project_role=project_coach,
                user=user_coach,
                team=team,
                active=True)
            coaches_users.append(user_coach)
        participant_users = []
        for team in self.project.teams.all():
            user_participant = self.get_user()
            UserProjectRole.objects.create(
                project_role=project_participant,
                user=user_participant,
                team=team,
                active=True)
            participant_users.append(user_participant)

        user_head_coach = self.get_user()
        UserProjectRole.objects.create(
            project_role=head_coach,
            user=user_head_coach,
            active=True)

        self.project._active_roles(self.super_user)

        # ASSERTS
        for user in coaches_users + participant_users + [user_head_coach]:
            self.assertEqual(
                list(get_project_for_user(user)),
                [self.project])

        self.assertEqual(
            list(get_team_for_user(self.project, user_head_coach)),
            list(self.project.teams.all()))

        for user in coaches_users:
            self.assertEqual(
                get_team_for_user(self.project, user).count(),
                1)
        for user in participant_users:
            self.assertEqual(
                get_team_for_user(self.project, user).count(),
                1)
