from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory
from utils.faker_factory import faker
from team.faker_factories.faker_factory_team import FakeTeamFactory

from ..user_title_helpers import get_user_title_in_project


class TestProjectUserTitle(TestCase):

    def setUp(self):
        super().setUp()
        self.sprint = FakeSprintAutomatedFactory.create()

    def test_manager_sprint(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )
        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)

        FakeConsultantProjectRoleFactory(
            consultant=consultant,
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=exo_role,
        )

        # DO ACTION
        user_title = get_user_title_in_project(self.sprint.project_ptr, consultant.user)

        # ASSERTS
        self.assertEqual(user_title, exo_role.name)

    def test_delivery_manager(self):
        #  PREPARE DATA
        super_user = FakeUserFactory(is_superuser=True)
        project = self.sprint.project_ptr

        # DO ACTION
        member = project.add_user_project_delivery_manager(
            super_user,
            faker.name(),
            faker.email(),
        )
        user_title = get_user_title_in_project(self.sprint.project_ptr, member)

        # ASSERTS
        self.assertEqual(user_title, ExORole.objects.get(code=settings.EXO_ROLE_CODE_DELIVERY_MANAGER).name)

    def test_coach_one_team(self):
        #  PREPARE DATA
        project = self.sprint.project_ptr
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        FakeTeamFactory.create(
            project=project,
            name='A',
            coach=consultant)

        # DO ACTION
        user_title = get_user_title_in_project(self.sprint.project_ptr, consultant.user)

        # ASSERTS
        self.assertEqual(user_title, 'A Sprint Coach')

    def test_coach_multiple_teams(self):
        #  PREPARE DATA
        project = self.sprint.project_ptr
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        FakeTeamFactory.create(
            project=project,
            name='A',
            coach=consultant)
        FakeTeamFactory.create(
            project=project,
            name='B',
            coach=consultant)

        # DO ACTION
        user_title = get_user_title_in_project(self.sprint.project_ptr, consultant.user)

        # ASSERTS
        self.assertEqual(user_title, 'A/B Sprint Coach')

    def test_participant_one_team(self):
        #  PREPARE DATA
        super_user = FakeUserFactory(is_superuser=True)
        project = self.sprint.project_ptr
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        team = FakeTeamFactory.create(
            project=project,
            name='A',
            coach=consultant)

        user = project.add_user_project_member(
            super_user, faker.email(), '123456')
        team.team_members.add(user)
        # DO ACTION
        user_title = get_user_title_in_project(self.sprint.project_ptr, user)

        # ASSERTS
        self.assertEqual(user_title, 'A Sprint Participant')

    def test_participant_multiple_teams(self):
        #  PREPARE DATA
        super_user = FakeUserFactory(is_superuser=True)
        project = self.sprint.project_ptr
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        team1 = FakeTeamFactory.create(
            project=project,
            name='A',
            coach=consultant)
        user = project.add_user_project_member(
            super_user, faker.email(), '123456')

        team2 = FakeTeamFactory.create(
            project=project,
            name='B',
            coach=consultant)
        team1.team_members.add(user)
        team2.team_members.add(user)

        # DO ACTION
        user_title = get_user_title_in_project(self.sprint.project_ptr, user)

        # ASSERTS
        self.assertEqual(user_title, 'A/B Sprint Participant')
