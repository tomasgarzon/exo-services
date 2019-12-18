from django.conf import settings

from rest_framework.test import APITestCase

from exo_role.models import ExORole

from consultant.faker_factories import FakeConsultantFactory
from customer.faker_factories import FakeCustomerFactory
from qa_session.faker_factories import FakeQASessionFactory
from project.faker_factories import FakeProjectFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin

from .models import CoreJob


class JobAPITestCase(SuperUserTestMixin, UserTestMixin, APITestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()
        self.client.login(
            username=self.user.username,
            password='123456',
        )
        self.consultant = FakeConsultantFactory.create(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)

    def create_consultant_project_role(self, exo_role):
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)
        return FakeConsultantProjectRoleFactory.create(
            consultant=self.consultant,
            project=project,
            exo_role=exo_role,
            visible=True,
            status=settings.RELATION_ROLE_CH_ACTIVE)

    def test_consultant_jobs_for_project_roles(self):

        for code in ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_EXO_SPRINT).values_list('code', flat=True):
            exo_role = ExORole.objects.get(code=code)

            # DO ACTION
            c_project_role = self.create_consultant_project_role(exo_role)

            # ASSERTS
            self.assertTrue(
                CoreJob.objects.all().filter_by_instance(c_project_role).exists()
            )

            # DO ACTION DELETE
            c_project_role.delete()

            # ASSERTS
            self.assertFalse(
                CoreJob.objects.all().filter_by_instance(c_project_role).exists()
            )

    def test_qa_session_jobs(self):
        # PREPARE DATA
        qa_session = FakeQASessionFactory.create()
        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR)
        c_project_role = self.create_consultant_project_role(exo_role)

        # DO ACTION
        qa_session_member = qa_session.qa_session_advisors.create(consultant_project_role=c_project_role)

        # ASSERTS
        self.assertTrue(
            CoreJob.objects.all().filter_by_instance(qa_session_member).exists()
        )

        # DO ACTION
        qa_session.qa_session_advisors.filter(consultant_project_role=c_project_role).delete()

        self.assertFalse(
            CoreJob.objects.all().filter_by_instance(qa_session_member).exists()
        )

    def test_jobs_for_projects_with_training_customer(self):
        # PREPARE DATA
        customer = FakeCustomerFactory.create(customer_type=settings.CUSTOMER_CH_TRAINING)
        project = FakeProjectFactory.create(
            customer=customer,
            status=settings.PROJECT_CH_PROJECT_STATUS_STARTED)

        for code in ExORole.objects.all().filter_by_category_code(
                settings.EXO_ROLE_CATEGORY_EXO_SPRINT).values_list('code', flat=True):
            exo_role = ExORole.objects.get(code=code)

            # DO ACTION
            c_project_role = FakeConsultantProjectRoleFactory.create(
                consultant=self.consultant,
                project=project,
                exo_role=exo_role,
                visible=True,
                status=settings.RELATION_ROLE_CH_ACTIVE)

            # ASSERTS
            self.assertTrue(
                CoreJob.objects.all().filter_by_instance(c_project_role).exists()
            )
