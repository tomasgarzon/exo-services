from django.core import mail
from django.utils import timezone
from django.test import TestCase

from utils.faker_factory import faker
from test_utils.test_case_mixins import SuperUserTestMixin
from customer.tests.test_mixins import TestCustomerMixin
from team.faker_factories import FakeTeamFactory


class InvitationLogTest(SuperUserTestMixin, TestCustomerMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.create_customer()

    def test_sprint_launch(self):
        sprint = self.customer.create_sprint_automated(
            self.super_user,
            faker.first_name(),
            start=timezone.now(),
            description='',
        )
        project = sprint.project_ptr

        new_user_email = faker.email()
        new_user_name = faker.name()
        team = FakeTeamFactory.create(
            project=sprint.project_ptr,
            user_from=self.super_user,
            coach__user__is_active=True,
        )
        member = team.add_member(
            user_from=self.super_user,
            email=new_user_email,
            name=new_user_name,
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
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(member.check_password(fixed_pass))
