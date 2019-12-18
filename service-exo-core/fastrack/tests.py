from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from consultant.faker_factories import FakeConsultantFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory
from relation.models import ConsultantProjectRole
from team.models import Team
from .faker_factories import FakeFastrackFactory


class FastrackTestCase(TestCase):

    def initialize_fastrack(self):
        fastrack = FakeFastrackFactory.create()
        project = fastrack.project_ptr

        role_team_leader = FakeConsultantProjectRoleFactory(
            consultant=FakeConsultantFactory(
                status=settings.CONSULTANT_STATUS_CH_ACTIVE,
            ),
            project=project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER),
        )
        role_curator = FakeConsultantProjectRoleFactory(
            consultant=FakeConsultantFactory(
                status=settings.CONSULTANT_STATUS_CH_ACTIVE,
            ),
            project=project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_FASTRACK_CURATOR),
        )
        return fastrack, project, role_team_leader, role_curator

    def test_roles(self):
        # PREPARE DATA
        fastrack, project, role_team_leader, role_curator = self.initialize_fastrack()

        # ASSERTS
        self.assertTrue(project.role_is_manager(role_curator.exo_role))
        self.assertTrue(project.role_is_team_manager(role_team_leader.exo_role))
        self.assertEqual(
            ConsultantProjectRole.objects.get_team_manager_consultants(project).count(),
            1)
        self.assertEqual(
            ConsultantProjectRole.objects.get_project_manager_consultants(project).count(),
            1)

    def test_change_team_leader(self):
        # PREPARE DATA
        fastrack, project, role_team_leader, role_curator = self.initialize_fastrack()
        team = Team.objects.create(
            project=project,
            user_from=role_curator.consultant.user,
            created_by=role_curator.consultant.user,
            name='name',
            coach=role_team_leader.consultant,
            stream=settings.PROJECT_STREAM_CH_STRATEGY,
            team_members=[],
        )
        new_role_team_leader = FakeConsultantProjectRoleFactory(
            consultant=FakeConsultantFactory(
                status=settings.CONSULTANT_STATUS_CH_ACTIVE,
            ),
            project=project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_FASTRACK_TEAM_LEADER),
        )
        # DO ACTION
        team = Team.objects.update(
            instance=team,
            user_from=role_curator.consultant.user,
            name='name2',
            coach=new_role_team_leader.consultant,
            zoom_id=None,
            stream=team.stream,
            team_members=[],
            collaborators=[],
        )
        # ASSERTS
        self.assertEqual(team.coach, new_role_team_leader.consultant)
        self.assertEqual(project.consultants_roles.count(), 3)
        self.assertEqual(
            ConsultantProjectRole.objects.filter_by_exo_role_code(
                settings.EXO_ROLE_CODE_SPRINT_COACH).filter_by_project(project).count(),
            0)
        self.assertNotEqual(
            new_role_team_leader.get_data_email(None),
            {})
