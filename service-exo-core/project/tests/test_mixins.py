from django.conf import settings

from utils.faker_factory import faker
from consultant.faker_factories import FakeConsultantFactory
from team.models import Team
from sprint_automated.faker_factories import FakeSprintAutomatedFactory

from ..faker_factories.faker_factory_project import FakeProjectFactory


class TestProjectMixin():

    def create_project(self, start=None):
        self.project = FakeProjectFactory.create(start=start)
        return self.project

    def _build_sprint(self, number_of_members=2):
        sprint = FakeSprintAutomatedFactory()
        team_members = [{
            'email': faker.email(),
            'short_name': faker.name(),
        } for _ in range(1, number_of_members + 1)]

        project = sprint.project_ptr
        consultant = FakeConsultantFactory()
        team = Team.objects.create(
            project=project,
            user_from=self.super_user,
            created_by=self.super_user,
            name=faker.name(),
            coach=consultant,
            stream=settings.PROJECT_STREAM_CH_STRATEGY,
            team_members=team_members,
        )
        return sprint, team, consultant
