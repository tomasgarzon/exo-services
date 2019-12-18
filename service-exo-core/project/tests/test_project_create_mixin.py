from django.conf import settings
from django.utils import timezone

from exo_role.models import ExORole

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from utils.faker_factory import faker


class TestProjectCreationMixin:

    def create_team_members(self, team, size):
        for _ in range(size):
            participant = team.add_member(
                user_from=self.super_user,
                email=faker.email(),
                name=faker.name(),
            )

            participant.set_password('123456')
            participant.save()

        self.user_coach = self.team.coach.user
        self.user_head_coach = self.team.project.project_manager.user
        self.user_team_member = self.team.team_members.all().first()

    def create_team(self):
        self.consultant_for_coach_role = FakeConsultantFactory.create(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        self.coach_role = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=self.project,
            consultant=self.consultant_for_coach_role,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        consultant_manager_user = FakeUserFactory.create(password='123456', is_active=True)
        self.consultant_for_manager_role = FakeConsultantFactory.create(
            user=consultant_manager_user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        self.manager_role = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=self.project,
            consultant=self.consultant_for_manager_role,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )

        self.team = FakeTeamFactory.create(
            coach=self.consultant_for_coach_role,
            project=self.project,
        )

        delivery_manager_user = FakeUserFactory.create(password='123456', is_active=True)
        self.delivery_manager = self.project.add_user_project_delivery_manager(
            self.super_user,
            delivery_manager_user.short_name,
            delivery_manager_user.email,
        )

    def create_project(self):
        self.sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING,
            start=timezone.now()
        )
        self.project = self.sprint.project_ptr

    def create_assignments(self):
        template = settings.PROJECT_CH_TEMPLATE_ASSIGNMENTS_SPRINT_BOOK
        self.project.update_assignments_template(template)
