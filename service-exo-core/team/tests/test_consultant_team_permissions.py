from django.test import TestCase

from exo_role.models import ExORole

from test_utils.test_case_mixins import SuperUserTestMixin
from relation.models import ConsultantProjectRole
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory

from ..conf import settings


class TestConsultantTeamPermission(SuperUserTestMixin, TestCase):
    """
    Test Consultants Team permissions related with Services
    (Sprint)
    """

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.consultant = FakeConsultantFactory(status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        self.sprint = FakeSprintAutomatedFactory(status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        # Sprint Teams
        self.team_s_a = FakeTeamFactory.create(project=self.sprint.project_ptr)
        self.team_s_b = FakeTeamFactory.create(project=self.sprint.project_ptr)

    # ##
    # Test for Team Coach
    # ##

    def test_permissions_at_create_team_with_coach(self):
        """
            Signal signal_team_coach_updated is lunched when creating a Team
            with a coach
        """
        team = FakeTeamFactory(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )

        self.assertTrue(self.consultant.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            team,
        ))
        self.assertTrue(self.consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            team,
        ))

    def test_permissions_when_updating_coach_for_team(self):
        """
            Change the Coach for this Team:
            - Old Coach: should not have permissions
            - New coach: shold have permissions
        """
        coach_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        new_team = FakeTeamFactory(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )

        new_consultant = FakeConsultantFactory(status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=new_consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        new_team.update_coach(
            user_from=self.super_user,
            coach=new_consultant,
        )

        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            new_team,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            new_team,
        ))

        self.assertTrue(new_consultant.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            new_team,
        ))
        self.assertTrue(new_consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            new_team,
        ))

    def test_permissions_for_coach_when_team_deleted(self):
        """
            Check permissions for coach when a Team is deleted
        """
        coach_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        new_team = FakeTeamFactory(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )
        new_team.delete()

        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            new_team,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            new_team,
        ))

    def test_permissions_for_coach_when_team_deleted_for_multiple_teams(self):
        """
            Check permissions for coach when a Team is deleted
        """
        coach_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        new_team_a = FakeTeamFactory(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )
        new_team_b = FakeTeamFactory(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )
        new_team_a.delete()

        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            new_team_a,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            new_team_a,
        ))

        self.assertTrue(self.consultant.user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM,
            new_team_b,
        ))
        self.assertTrue(self.consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            new_team_b,
        ))

    def test_permissions_when_delete_consultant_as_coach_from_team(self):
        """
            Check permissions for a Consultor that is Collaborator and Coach
            and is deleted as Coach
        """
        new_consultant = FakeConsultantFactory(status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=new_consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        new_team = FakeTeamFactory(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )

        new_team.update_coach(
            user_from=self.super_user,
            coach=new_consultant,
        )

        self.assertFalse(self.consultant.user.has_perm(
            settings.TEAM_PERMS_COACH_TEAM,
            new_team,
        ))
