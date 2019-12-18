from django.test import TestCase

from exo_role.models import ExORole

from consultant.faker_factories import FakeConsultantFactory
from project.faker_factories import FakeProjectFactory
from test_utils.test_case_mixins import SuperUserTestMixin

from ..conf import settings
from ..faker_factories import FakeConsultantProjectRoleFactory
from ..models import ConsultantProjectRole


class ConsultantProjectRoleTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        self.consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )
        self.project = FakeProjectFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)

    def test_create(self):

        # ##
        # Test Faker
        # ##

        relation = FakeConsultantProjectRoleFactory(
            consultant=self.consultant,
            project=self.project,
        )

        self.assertIsNotNone(relation)

        # ##
        # Test with the model create method
        # ##

        relation = ConsultantProjectRole.objects.get(
            consultant=self.consultant,
            project=self.project,
        )

        self.assertIsNotNone(relation)
        self.assertIsNotNone(relation.exo_role)

    def test_get_or_create_coach(self):

        consultant_project_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )

        self.assertIsNotNone(consultant_project_role)
        self.assertTrue(created)
        self.assertEqual(
            consultant_project_role.exo_role.code,
            settings.EXO_ROLE_CODE_SPRINT_COACH
        )

    def test_get_coach_consultants(self):

        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.project,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
        )
        # Assert the consultant has the role of coach at the
        #  ConsultantProjectRole of the Sprint
        self.assertEqual(
            ConsultantProjectRole.objects.all()
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_COACH)
            .filter_by_project(self.project)[0].consultant,
            self.consultant,
        )
        self.assertTrue(
            self.consultant in ConsultantProjectRole.objects.all()
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_COACH)
            .filter_by_project(self.project)
            .consultants()
        )

    def test_manager_filter(self):

        FakeConsultantProjectRoleFactory(
            consultant=self.consultant,
            project=self.project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )
        self.assertTrue(ConsultantProjectRole.objects.actives().count(), 1)
        self.assertTrue(ConsultantProjectRole.objects.actives().projects().count(), 1)
        self.assertTrue(ConsultantProjectRole.objects.actives().consultants().count(), 1)
        FakeConsultantProjectRoleFactory(
            consultant=self.consultant,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR)
        )
        self.assertTrue(ConsultantProjectRole.objects.actives().projects().count(), 2)
        self.assertTrue(ConsultantProjectRole.objects.actives().consultants().count(), 2)
        self.assertEqual(self.consultant.get_projects().count(), 2)
        FakeConsultantProjectRoleFactory(
            consultant=self.consultant,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR)
        )
        self.assertTrue(
            self.consultant.get_projects(
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
            ).count() >= 1,
        )

    def test_actives_filter(self):

        project = FakeProjectFactory()
        consultant_1 = FakeConsultantFactory(user__is_active=True)
        consultant_2 = FakeConsultantFactory(user__is_active=True)

        self.assertTrue(consultant_1.user.is_active)
        self.assertTrue(consultant_2.user.is_active)

        # Create another project to check filter
        relation_p_1 = FakeConsultantProjectRoleFactory(
            consultant=consultant_1,
            project=project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )
        self.assertIsNotNone(relation_p_1)
        relation_p_2 = FakeConsultantProjectRoleFactory(
            consultant=consultant_2,
            project=project,
            status=settings.RELATION_ROLE_CH_INACTIVE,
        )
        self.assertIsNotNone(relation_p_2)

        # ##
        # Work with self.project
        # ##
        relation_1 = FakeConsultantProjectRoleFactory(
            consultant=consultant_1,
            project=self.project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )
        self.assertIsNotNone(relation_1)

        relation_2 = FakeConsultantProjectRoleFactory(
            consultant=consultant_2,
            project=self.project,
            status=settings.RELATION_ROLE_CH_INACTIVE,
        )
        self.assertIsNotNone(relation_2)

        self.assertEqual(self.project.consultants_roles.actives().count(), 1)
        self.assertEqual(ConsultantProjectRole.objects.actives().count(), 2)

        relation_2.activate(consultant_2.user)
        self.assertEqual(self.project.consultants_roles.count(), 2)
        self.assertEqual(self.project.consultants_roles.actives().count(), 2)
        self.assertEqual(ConsultantProjectRole.objects.actives().count(), 3)
        self.assertEqual(ConsultantProjectRole.objects.count(), 4)
