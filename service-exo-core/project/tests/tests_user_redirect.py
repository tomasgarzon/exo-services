from django import test
from django.conf import settings

from exo_role.models import ExORole

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from relation.models import ConsultantProjectRole
from project.faker_factories import FakeProjectFactory
from team.faker_factories import FakeTeamFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..helpers import next_project_url


class TestConsultantRedirectController(
        UserTestMixin,
        SuperUserTestMixin,
        test.TestCase
):

    def setUp(self):
        self.create_user()
        self.create_superuser()

    def test_superuser(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        FakeTeamFactory.create(project=project)

        # ASSERTS
        url, _ = next_project_url(project, self.super_user)

        expected_url = project.get_absolute_url()

        self.assertEqual(
            url, expected_url,
            'Superuser',
        )

    def test_staff_user(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        FakeTeamFactory.create(project=project)
        exo_staff_user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            is_staff=True)
        project.add_user_project_staff(
            self.super_user,
            exo_staff_user.short_name,
            exo_staff_user.email)

        # ASSERTS
        url, _ = next_project_url(project, exo_staff_user)
        expected_url = ''
        self.assertEqual(
            url, expected_url,
            'Staff',
        )

    def test_coach_project_several_teams(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_STARTED,
            start=None)

        FakeTeamFactory.create(project=project)
        team = FakeTeamFactory.create(project=project)
        relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=project,
            consultant=team.coach,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        # ASSERTS
        url, _ = next_project_url(project, relation.consultant.user)
        expected_url = settings.FRONTEND_PROJECT_STEP_PAGE.format(
            **{
                'project_id': project.id,
                'team_id': team.pk,
                'step_id': project.steps.first().pk,
                'section': 'learn'})

        self.assertEqual(url, expected_url)
