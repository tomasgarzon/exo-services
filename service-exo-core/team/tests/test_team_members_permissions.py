from django.test import TestCase

from exo_role.models import ExORole

from utils.faker_factory import faker
from test_utils.test_case_mixins import SuperUserTestMixin
from project.faker_factories import FakeProjectFactory
from relation.models import ConsultantProjectRole
from consultant.faker_factories import FakeConsultantFactory

from ..conf import settings
from ..faker_factories.faker_factory_team import FakeTeamFactory


class TeamMemberPermissionTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.project = FakeProjectFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)

    def test_user_member_permissions(self):
        """
        Test for TeamManager create method
        """
        user_email = faker.email()
        user_name = faker.name()

        team = FakeTeamFactory.create(project=self.project)

        member = team.add_member(
            user_from=self.super_user,
            email=user_email,
            name=user_name,
        )

        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            self.project,
        ))
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team,
        ))

        team.remove_member(self.super_user, member)

        self.assertFalse(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            self.project,
        ))
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team,
        ))

    def test_user_member_multiple_teams_permissions(self):
        """
            Add user to multiple Teams for the same Service
            and check permissions for this Team and Service
        """
        user_email = faker.email()
        user_name = faker.name()

        team_a = FakeTeamFactory.create(project=self.project)
        team_b = FakeTeamFactory.create(project=self.project)

        member = team_a.add_member(
            user_from=self.super_user,
            email=user_email,
            name=user_name,
        )

        team_b.add_member(
            user_from=self.super_user,
            email=user_email,
            name=user_name,
        )

        team_a.remove_member(self.super_user, member)

        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            self.project,
        ))
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team_a,
        ))

        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            self.project,
        ))
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team_b,
        ))

        team_b.remove_member(self.super_user, member)

        self.assertFalse(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            self.project,
        ))
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team_b,
        ))

    def test_permissions_for_user_added_for_twice(self):
        """
            Add an User for 2 times as TeamMember and check permissions
        """

        user_email = faker.email()
        user_name = faker.name()

        team = FakeTeamFactory.create(project=self.project)

        member = team.add_member(
            user_from=self.super_user,
            email=user_email,
            name=user_name,
        )
        team.remove_member(self.super_user, member)

        self.assertEqual(team.team_members.filter(email=user_email).count(), 0)

        member = team.add_member(
            user_from=self.super_user,
            email=user_email,
            name=user_name,
        )

        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team,
        ))
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            self.project,
        ))

    def test_manager_can_edit_participants_profile(self):
        team = FakeTeamFactory.create(project=self.project)
        member = team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )
        relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=team.project,
            consultant=FakeConsultantFactory(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )
        self.assertTrue(
            relation.consultant.user.has_perm(
                settings.EXO_ACCOUNTS_PERMS_USER_EDIT,
                member))

        # add a new member
        member2 = team.add_member(
            user_from=relation.consultant.user,
            email=faker.email(),
            name=faker.name(),
        )

        has_perm = relation.consultant.user.has_perm(
            settings.EXO_ACCOUNTS_PERMS_USER_EDIT,
            member2)
        self.assertTrue(has_perm)

        team.remove_member(relation.consultant.user, member2)
        self.assertFalse(
            relation.consultant.user.has_perm(
                settings.EXO_ACCOUNTS_PERMS_USER_EDIT,
                member2))
