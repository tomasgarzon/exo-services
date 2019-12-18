from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from project.faker_factories import FakeProjectFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from team.faker_factories import FakeTeamFactory
from team.models import Team
from relation.models import ConsultantProjectRole
from consultant.faker_factories import FakeConsultantFactory


class ConsultantProjectRoleTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        super().setUp()

    def test_create_reporter(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)

        FakeTeamFactory.create_batch(size=3, project=project)

        # DO ACTION
        relation, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            consultant=FakeConsultantFactory.create(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_REPORTER)
        )

        # ASSERTS
        member = relation.consultant.user
        self.assertTrue(member.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT, project))
        self.assertTrue(member.has_perm(settings.PROJECT_PERMS_ONLY_VIEW_PROJECT, project))

        teams = Team.objects.filter_by_project(project).filter_by_user(project, member)
        self.assertEqual(teams.count(), 3)
