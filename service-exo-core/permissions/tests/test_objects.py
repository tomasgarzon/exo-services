from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory
from utils.faker_factory import faker

from ..objects import get_team_for_user


class ShortcutTestCase(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_get_team_for_user(self):
        manager1 = FakeConsultantFactory.create(user__is_active=True)
        manager2 = FakeConsultantFactory.create(user__is_active=True)
        sprint = FakeSprintAutomatedFactory.create()
        sprint2 = FakeSprintAutomatedFactory.create()

        FakeConsultantProjectRoleFactory(
            consultant=manager1,
            project=sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )
        FakeConsultantProjectRoleFactory(
            consultant=manager2,
            project=sprint2.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )

        coach1 = FakeConsultantFactory.create(user__is_active=True)
        teams_1 = FakeTeamFactory.create_batch(
            size=3,
            user_from=self.super_user,
            project=sprint.project_ptr,
        )
        teams_2 = FakeTeamFactory.create_batch(
            size=2,
            user_from=self.super_user,
            project=sprint2.project_ptr,
            coach=coach1,
        )
        sprint.project_ptr.launch(self.super_user)
        sprint2.project_ptr.launch(self.super_user)

        self.assertEqual(
            get_team_for_user(
                sprint.project_ptr,
                self.super_user,
            ).count(), 3,
        )
        self.assertEqual(
            get_team_for_user(
                sprint2.project_ptr,
                self.super_user,
            ).count(), 2,
        )
        self.assertEqual(
            get_team_for_user(
                sprint.project_ptr,
                manager2.user,
            ).count(), 0,
        )
        self.assertEqual(
            get_team_for_user(
                sprint2.project_ptr,
                manager1.user,
            ).count(), 0,
        )
        self.assertEqual(
            get_team_for_user(
                sprint.project_ptr,
                teams_1[0].coach.user,
            ).count(), 1,
        )
        self.assertEqual(
            get_team_for_user(
                sprint.project_ptr,
                teams_1[0].coach.user,
            ).count(), 1,
        )
        self.assertEqual(
            get_team_for_user(
                sprint2.project_ptr,
                coach1.user,
            ).count(), 2,
        )

        member1 = teams_1[0].add_member(
            user_from=self.super_user,
            name=faker.first_name(),
            email=faker.email(),
        )
        member2 = teams_2[0].add_member(
            user_from=self.super_user,
            name=faker.first_name(),
            email=faker.email(),
        )
        self.assertEqual(
            get_team_for_user(
                sprint.project_ptr,
                member1,
            ).count(), 1,
        )
        self.assertEqual(
            get_team_for_user(
                sprint2.project_ptr,
                member2,
            ).count(), 1,
        )
