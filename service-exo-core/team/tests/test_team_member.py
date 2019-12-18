from django.test import TestCase

from mock import patch

from exo_role.models import ExORole

from utils.faker_factory import faker
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from test_utils.test_case_mixins import SuperUserTestMixin
from sprint.faker_factories.faker_factory_sprint import FakeSprintAutomatedFactory
from project.signals_define import project_post_launch

from ..conf import settings
from ..faker_factories.faker_factory_team import FakeTeamFactory
from ..models import Team


class TeamMemberTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.receivers = project_post_launch.receivers.copy()
        project_post_launch.receivers = []

    def tearDown(self):
        project_post_launch.receivers = self.receivers

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_create_team_from_manager(self, mock_handler):
        # PREPARE DATA
        team_members = [{
            'email': faker.email(),
            'short_name': faker.name(),
        } for _ in range(1, 3)]

        sprint = FakeSprintAutomatedFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project = sprint.project_ptr
        consultant = FakeConsultantFactory()

        # DO ACTION
        team = Team.objects.create(
            project=project,
            user_from=self.super_user,
            created_by=self.super_user,
            name='name',
            coach=consultant,
            stream=settings.PROJECT_STREAM_CH_STRATEGY,
            team_members=team_members,
        )

        # ASSERTS
        self.assertFalse(mock_handler.called)

        self.assertIsNotNone(team)
        self.assertIsNotNone(team.project)
        self.assertIsNotNone(team.name)
        self.assertIsNotNone(team.stream)
        self.assertTrue(team.stream in [
            x[0]
            for x in settings.PROJECT_STREAM_CH_TYPE
        ])
        self.assertIsNotNone(team.coach)
        self.assertIsNotNone(team.team_members.all())
        member_manager = team.members
        self.assertIsNotNone(member_manager)
        team_member = member_manager.get_by_user(team.team_members.first())
        self.assertIsNotNone(team_member)
        self.assertEqual(team_member.user, team.team_members.first())

    def test_coach_consultant_role(self):
        sprint = FakeSprintAutomatedFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        consultant = FakeConsultantFactory(user__is_active=True)

        Team.objects.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            created_by=self.super_user,
            name=faker.name(),
            coach=consultant,
            stream=settings.PROJECT_STREAM_CH_STRATEGY,
        )
        sprint.refresh_from_db()

        self.assertEqual(
            sprint.consultants.all()[0],
            consultant,
        )

    @patch('exo_accounts.models.User.send_notification')
    def test_add_new_unexisting_user_to_team(
        self,
        user_notification_sent,
    ):
        new_team = FakeTeamFactory.create(project__status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        new_user_email = faker.email()
        new_user_name = faker.name()
        member = new_team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
        )

        self.assertFalse(user_notification_sent.called)
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT, new_team.project,
        ))
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_COACH_TEAM, new_team,
        ))

    def test_coach_consultant_change(self):
        sprint = FakeSprintAutomatedFactory(status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        consultant = FakeConsultantFactory(user__is_active=True)
        consultant2 = FakeConsultantFactory(user__is_active=True)

        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=consultant2,
            project=sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        new_team = Team.objects.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            created_by=self.super_user,
            name=faker.name(),
            coach=consultant,
            stream=settings.PROJECT_STREAM_CH_STRATEGY,
        )
        member = consultant.user
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_COACH_TEAM, new_team,
        ))
        new_team.update_coach(
            self.super_user,
            consultant2,
        )

        member2 = consultant2.user
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_COACH_TEAM, new_team,
        ))
        self.assertTrue(member2.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(member2.has_perm(
            settings.TEAM_PERMS_COACH_TEAM, new_team,
        ))
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT, new_team.project,
        ))

    def test_remove_user_to_team(self):
        new_team = FakeTeamFactory.create(project__status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        user = FakeUserFactory.create(is_active=True)
        new_user_email = user.email
        new_user_name = user.short_name
        new_team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
        )
        self.assertTrue(user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(user.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT, new_team.project,
        ))
        user2 = new_team.get_member(new_user_email)
        self.assertEqual(user2, user)
        new_team.remove_member(self.super_user, user)
        user2 = new_team.get_member(new_user_email)
        self.assertIsNone(user2)
        self.assertFalse(user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertFalse(user.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT, new_team.project,
        ))

    def test_remove_team(self):
        new_team = FakeTeamFactory.create(project__status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        project = new_team.project
        user = FakeUserFactory.create(is_active=True)
        new_user_email = user.email
        new_user_name = user.short_name
        new_team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
        )
        self.assertTrue(user.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(user.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT, new_team.project,
        ))
        new_team.delete()
        self.assertFalse(user.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT, project,
        ))

    def test_update_members(self):
        new_team = FakeTeamFactory.create(project__status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        users = FakeUserFactory.create_batch(size=4, is_active=True)
        member = new_team.add_member(
            user_from=self.super_user,
            email=users[0].email,
            name=users[0].short_name,
        )
        self.assertTrue(member in new_team.team_members.all())
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        new_members = []
        new_members.append({'email': users[1].email, 'short_name': users[1].short_name})
        new_members.append({'email': users[2].email, 'short_name': users[2].short_name})
        new_team.update_members(
            self.super_user,
            new_members,
        )
        self.assertFalse(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(users[1].has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(users[2].has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        member = new_team.add_member(
            user_from=self.super_user,
            email=users[3].email,
            name=users[3].short_name,
        )
        new_members.append({'email': users[3].email, 'short_name': users[3].short_name})
        new_team.update_members(
            self.super_user,
            new_members,
        )
        self.assertTrue(member.has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(users[1].has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertTrue(users[2].has_perm(
            settings.TEAM_PERMS_FULL_VIEW_TEAM, new_team,
        ))
        self.assertEqual(new_team.team_members.all().count(), 3)

    def test_add_members_with_fixed_password(self):
        new_team = FakeTeamFactory.create(project__status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        project_settings = new_team.project.settings
        project_settings.launch['fix_password'] = '123456'
        project_settings.save()
        user = FakeUserFactory.create(is_active=True, password='aaa')
        member = new_team.add_member(
            user_from=self.super_user,
            email=user.email,
            name=user.short_name,
        )
        self.assertTrue(member.check_password('aaa'))  # maintain previous password
        member2 = new_team.add_member(
            user_from=self.super_user,
            email=faker.email(),
            name=faker.name(),
        )
        self.assertTrue(member2.check_password('123456'))  # set password by project
