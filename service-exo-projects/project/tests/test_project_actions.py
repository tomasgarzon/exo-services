from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin
from .. import models


class ProjectActionsTest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(
            created_by=cls.super_user,
            start=timezone.now().date())

    def setUp(self):
        super().setUp()
        self.project.refresh_from_db()

    def test_project_user_actions(self):
        # PREPARE DATA

        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            teams=self.project.teams.all(),
            user=user)

        user_participant = models.UserProjectRole.objects.create_participant(
            project=self.project,
            teams=self.project.teams.all(),
            name=faker.name(),
            email=faker.email()).user

        # ASSERTS before launch
        self.assertSetEqual(
            set(self.project.user_actions_for_user(self.project.created_by, user)),
            set([
                settings.PROJECT_CH_ACTION_USER_EDIT_ROLES,
                settings.PROJECT_CH_ACTION_USER_UNSELECT]))
        self.assertSetEqual(
            set(self.project.user_actions_for_user(self.project.created_by, user_participant)),
            set([
                settings.PROJECT_CH_ACTION_USER_EDIT_PARTICIPANT,
                settings.PROJECT_CH_ACTION_USER_UNSELECT]))

        # DO ACTION
        self.project._active_roles(self.super_user)

        # ASSERTS after launch
        self.assertSetEqual(
            set(self.project.user_actions_for_user(self.project.created_by, user)),
            set([
                settings.PROJECT_CH_ACTION_USER_EDIT_ROLES,
                settings.PROJECT_CH_ACTION_USER_UNSELECT]))
        self.assertSetEqual(
            set(self.project.user_actions_for_user(self.project.created_by, user_participant)),
            set([
                settings.PROJECT_CH_ACTION_USER_EDIT_TEAMS,
                settings.PROJECT_CH_ACTION_USER_UNSELECT]))

    def test_team_user_actions(self):
        # PREPARE DATA
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            teams=self.project.teams.all(),
            user=user)
        user_team_role = user.user_team_roles.first()

        user_participant = models.UserProjectRole.objects.create_participant(
            project=self.project,
            teams=self.project.teams.all(),
            name=faker.name(),
            email=faker.email()).user
        user_team_role_participant = user_participant.user_team_roles.first()

        # ASSERTS before launch
        self.assertSetEqual(
            set(user_team_role.user_actions(self.project.created_by)),
            set([
                settings.TEAM_CH_ACTION_USER_TEAM_EDIT_ROLES,
                settings.TEAM_CH_ACTION_USER_TEAM_UNSELECT,
                settings.TEAM_CH_ACTION_USER_TEAM_MOVE]))
        self.assertSetEqual(
            set(user_team_role_participant.user_actions(self.project.created_by)),
            set([
                settings.TEAM_CH_ACTION_USER_TEAM_EDIT_PARTICIPANT,
                settings.TEAM_CH_ACTION_USER_TEAM_UNSELECT,
                settings.TEAM_CH_ACTION_USER_TEAM_MOVE]))

        # DO ACTION
        self.project._active_roles(self.super_user)
        user_team_role.refresh_from_db()
        user_team_role_participant.refresh_from_db()

        # ASSERTS after launch
        self.assertSetEqual(
            set(user_team_role.user_actions(self.project.created_by)),
            set([
                settings.TEAM_CH_ACTION_USER_TEAM_EDIT_ROLES,
                settings.TEAM_CH_ACTION_USER_TEAM_UNSELECT,
                settings.TEAM_CH_ACTION_USER_TEAM_MOVE]))
        self.assertSetEqual(
            set(user_team_role_participant.user_actions(self.project.created_by)),
            set([
                settings.TEAM_CH_ACTION_USER_TEAM_EDIT_TEAMS,
                settings.TEAM_CH_ACTION_USER_TEAM_UNSELECT,
                settings.TEAM_CH_ACTION_USER_TEAM_MOVE]))
