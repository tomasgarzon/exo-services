from django.conf import settings
from django.test import TestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin
from ..user_title_helper import get_user_title_in_project


class ProjectuserTitleAPITest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def test_collaborator_without_team(self):
        # PREPARE DATA
        roles = [settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH, 'SAS', settings.EXO_ROLE_CODE_SPRINT_COACH]
        user = self.get_user()
        for role_code in roles:
            role = self.project.project_roles.get(code=role_code)
            models.UserProjectRole.objects.create(
                project_role=role,
                user=user)

        text_expected = 'Awake Speaker, Head Coach, Sprint Coach'
        # DO ACTION
        text_user_title = get_user_title_in_project(self.project, user)

        # ASSERTS
        self.assertEqual(text_expected, text_user_title)

    def test_collaborator_with_team(self):
        # PREPARE DATA
        roles = [settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH, 'SAS']
        user = self.get_user()
        for role_code in roles:
            role = self.project.project_roles.get(code=role_code)
            models.UserProjectRole.objects.create(
                project_role=role,
                user=user)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            teams=[self.project.teams.first()],
            user=user)

        text_expected = 'Awake Speaker, Head Coach, Sprint Coach'
        text_expected_team = 'Awake Speaker, Head Coach, {} Coach'.format(self.project.teams.first().name)

        # DO ACTION
        text_user_title = get_user_title_in_project(self.project, user)
        text_user_title_team = get_user_title_in_project(self.project, user, self.project.teams.first())

        # ASSERTS
        self.assertEqual(text_expected, text_user_title)
        self.assertEqual(text_expected_team, text_user_title_team)

    def test_participant_with_team(self):
        # PREPARE DATA
        user_role = models.UserProjectRole.objects.create_participant(
            project=self.project,
            teams=[self.project.teams.first()],
            name=faker.name(),
            email=faker.email())
        user = user_role.user

        text_expected = 'Sprint Participant'
        text_expected_team = '{} Participant'.format(self.project.teams.first().name)

        # DO ACTION
        text_user_title = get_user_title_in_project(self.project, user)
        text_user_title_team = get_user_title_in_project(self.project, user, self.project.teams.first())

        # ASSERTS
        self.assertEqual(text_expected, text_user_title)
        self.assertEqual(text_expected_team, text_user_title_team)
