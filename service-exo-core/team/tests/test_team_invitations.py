from django.test import TestCase
from django.core.exceptions import ValidationError
from django.conf import settings

from mock import patch

from exo_role.models import ExORole

from utils.faker_factory import faker
from utils.mail import handlers  # noqa
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from project.faker_factories import FakeProjectFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from invitation.models import Invitation
from sprint.faker_factories.faker_factory_sprint import FakeSprintAutomatedFactory

from ..faker_factories.faker_factory_team import FakeTeamFactory
from ..models import Team


class TeamInvitationsTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.project = FakeProjectFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)

    def test_create_team_invitations_with_members(self):

        member_list = [{'email': faker.email(), 'short_name': faker.name()}
                       for _ in range(2)]

        sprint = FakeSprintAutomatedFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project = sprint.project_ptr
        coach = FakeConsultantFactory(user__is_active=True)
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=coach,
            project=project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )
        team = Team.objects.create(
            user_from=self.super_user,
            created_by=self.super_user,
            project=project,
            name=faker.name(),
            coach=coach,
            stream=settings.PROJECT_STREAM_CH_STARTUP,
            team_members=member_list,
        )

        self.assertIsNotNone(team)
        self.assertEqual(
            Invitation.objects.filter(type=settings.INVITATION_TYPE_TEAM).count(),
            3,
        )

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_create_team_invitations(self, mock_handler):
        team = FakeTeamFactory(project__status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)

        self.assertIsNotNone(team)
        self.assertIsNotNone(team.coach)

        self.assertEqual(team.team_members.count(), 0)
        self.assertEqual(mock_handler.call_count, 0)
        self.assertEqual(
            Invitation.objects.filter(type=settings.INVITATION_TYPE_TEAM).count(),
            1,
        )

        invitation = Invitation.objects.filter(type=settings.INVITATION_TYPE_TEAM)[0]
        self.assertEqual(
            invitation.user,
            team.coach.user,
        )

        team.add_member(
            self.super_user,
            faker.email(),
            faker.name(),
        )

        self.assertEqual(team.team_members.count(), 1)
        # Inviations sent:
        #   - 1 simple sign up for new member
        #   - 1 user project
        #   - 2 team invitaions
        self.assertEqual(Invitation.objects.count(), 4)
        self.assertEqual(mock_handler.call_count, 0)

        self.assertEqual(
            Invitation.objects.filter(type=settings.INVITATION_TYPE_TEAM).count(),
            2,
        )

    def test_update_coach_invitations(self):

        team = FakeTeamFactory(project__status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project = FakeProjectFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        team_coach = team.coach

        new_coach = FakeConsultantFactory()
        with self.assertRaises(ValidationError):
            team.update_coach(
                self.super_user,
                new_coach,
            )

        self.assertEqual(team_coach, team.coach)

        new_project_coach = FakeConsultantFactory(user__is_active=True)
        speaker = FakeConsultantFactory(user__is_active=True)

        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=new_project_coach,
            project=project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=speaker,
            project=project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_AWAKE_SPEAKER),
        )

        with self.assertRaises(ValidationError):
            team.update_coach(
                self.super_user,
                new_coach,
            )

        with self.assertRaises(ValidationError):
            team.update_coach(
                self.super_user,
                speaker,
            )

        with self.assertRaises(ValidationError):
            team.update_coach(
                self.super_user,
                self.super_user,
            )

        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=new_project_coach,
            project=team.project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        team.update_coach(
            self.super_user,
            new_project_coach,
        )

        self.assertNotEqual(team_coach, team.coach)
        self.assertEqual(Invitation.objects.count(), 6)

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

        new_user = team_b.add_member(
            user_from=self.super_user,
            email=user_email,
            name=user_name,
        )

        self.assertEqual(new_user.projects_member.count(), 1)
        self.assertEqual(
            Invitation.objects.filter_by_object(
                new_user.projects_member.all()[0],
            ).count(), 1,
        )

        team_a.remove_member(self.super_user, member)

        self.assertEqual(new_user.projects_member.count(), 1)
        self.assertEqual(
            Invitation.objects.filter_by_object(
                new_user.projects_member.all()[0],
            ).count(), 1,
        )
