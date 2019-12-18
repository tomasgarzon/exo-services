from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from django.test import TestCase

from utils.faker_factory import faker
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from customer.tests.test_mixins import TestCustomerMixin
from team.faker_factories import FakeTeamFactory
from invitation.models import Invitation

from ..faker_factories import FakeProjectFactory


class ProjectLaunchTestCase(
        TestCustomerMixin,
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_customer()

    def test_sprint_launch(self):
        sprint = self.customer.create_sprint_automated(
            self.super_user,
            faker.first_name(),
            start=timezone.now(),
            description='',
        )
        project = sprint.project_ptr
        team = FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )
        new_user_email = faker.email()
        new_user_name = faker.name()

        member = team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
        )

        FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )

        project_setting = project.settings
        fixed_pass = faker.password()
        project_setting.launch['send_welcome_participant'] = False
        project_setting.launch['send_welcome_consultant'] = True
        project_setting.launch['fix_password'] = fixed_pass
        project_setting.save()
        mail.outbox = []
        project.launch(self.super_user, start_date=timezone.now())
        member.refresh_from_db()
        # we only send two emails for each coach in these teams
        self.assertEqual(len(mail.outbox), 2)
        self.assertTrue(member.check_password(fixed_pass))

    def test_sprint_launch_default(self):
        sprint = self.customer.create_sprint_automated(
            self.super_user,
            faker.first_name(),
            start=timezone.now(),
            description='',
        )
        project = sprint.project_ptr
        team = FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )
        new_user_email = faker.email()
        new_user_name = faker.name()

        member = team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
        )

        FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )

        project_setting = project.settings
        project_setting.launch['send_welcome_participant'] = True
        project_setting.launch['send_welcome_consultant'] = True
        project_setting.save()

        mail.outbox = []
        project.launch(self.super_user, start_date=timezone.now())
        member.refresh_from_db()
        # 2 coach more 1 member
        self.assertEqual(len(mail.outbox), 3)
        self.assertFalse(member.password_updated)

    def test_lauch_project_and_check_team_invitations(self):

        project = FakeProjectFactory()
        users = [{'email': faker.email(), 'name': faker.first_name()}
                 for _ in range(2)]

        team = FakeTeamFactory(project=project)

        team.update_members(self.super_user, members=users)
        for team_member in team.team_members.all():
            team_member_team_invitation = Invitation.objects.filter_by_object(team) \
                                                            .filter(user=team_member)
            self.assertEqual(team_member_team_invitation.count(), 1)
            self.assertTrue(team_member_team_invitation.first().is_pending)

        self.assertFalse(project.autoactive)
        project.launch(self.super_user, start_date=timezone.now())
        self.assertTrue(project.autoactive)

        for team_member in team.team_members.all():
            team_member_team_invitation = Invitation.objects.filter_by_object(team) \
                                                            .filter(user=team_member)
            self.assertEqual(team_member_team_invitation.count(), 1)
            self.assertTrue(team_member_team_invitation.first().is_active)

        project.set_started(self.super_user, timezone.now())

        for team_member in team.team_members.all():
            team_member_team_invitation = Invitation.objects.filter_by_object(team) \
                                                            .filter(user=team_member)
            self.assertEqual(team_member_team_invitation.count(), 1)
            self.assertTrue(team_member_team_invitation.first().is_active)

        # ##
        # Add a new Member and test SignUp invitaion is active
        # ##

        new_user = {'email': faker.email(), 'name': faker.first_name()}
        team.update_members(user_from=self.super_user, members=[new_user])
        new_member = get_user_model().objects.get(email=new_user.get('email'))

        team_member_team_invitation = Invitation.objects.filter_by_object(team) \
                                                        .filter(user=new_member)
        self.assertEqual(team_member_team_invitation.count(), 1)
        self.assertTrue(team_member_team_invitation.first().is_active)
