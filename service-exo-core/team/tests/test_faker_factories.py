from django.test import TestCase

from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeTeamFactory
from ..conf import settings


class FakeTeamTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_create_team_factory(self):
        team = FakeTeamFactory(
            user_from=self.super_user,
            coach__user__is_active=True,
        )

        self.assertIsNotNone(team)
        self.assertIsNotNone(team.project)
        self.assertIsNotNone(team.name)
        self.assertIsNotNone(team.stream)
        self.assertTrue(team.stream in dict(settings.PROJECT_STREAM_CH_TYPE).keys())
        self.assertIsNotNone(team.coach)
        self.assertTrue(team.coach.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, team,
        ))
        self.assertTrue(team.coach.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM, team,
        ))

    def test_delete_team(self):
        new_team = FakeTeamFactory(
            user_from=self.super_user,
            coach__user__is_active=True,
        )
        member = new_team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.first_name(),
        )
        coach = new_team.coach

        new_team.delete()
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertFalse(coach.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertFalse(coach.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM, new_team,
        ))
