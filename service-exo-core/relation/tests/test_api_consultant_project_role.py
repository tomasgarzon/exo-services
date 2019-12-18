from django.urls import reverse
from django.conf import settings

from rest_framework import status

from exo_role.models import ExORole

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import (
    SuperUserTestMixin, UserTestMixin
)
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from invitation.models import Invitation

from ..faker_factories import FakeConsultantProjectRoleFactory
from ..models import ConsultantProjectRole


class ConsultantProjectRoleTest(
        UserTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create()
        self.sprint = FakeSprintAutomatedFactory.create()

    def test_consultant_role_valid(self):
        c2 = FakeConsultantFactory.create()
        url = reverse(
            'api:relation:project:consultantprojectrole-list',
            kwargs={'project_id': self.sprint.project_ptr.pk},
        )
        data = {
            'consultant': c2.pk,
            'exo_role': ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH).pk,
        }
        self.client.login(username=self.super_user.email, password='123456')
        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        consultant_project_roles_coach = ConsultantProjectRole.objects \
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_COACH) \
            .filter_by_project(self.sprint.project_ptr)
        self.assertEqual(consultant_project_roles_coach.count(), 1)
        self.assertEqual(consultant_project_roles_coach.actives_only().count(), 0)

        c_project_role = consultant_project_roles_coach[0]
        self.assertEqual(Invitation.objects.filter_by_object(c_project_role).count(), 1)

        invitation = Invitation.objects.filter_by_object(c_project_role)[0]
        self.assertTrue(invitation.is_pending)
        self.assertFalse(
            c2.user.has_perm(
                settings.PROJECT_PERMS_VIEW_PROJECT,
                self.sprint.project_ptr,
            ),
        )
        self.assertEqual(response.data['pk'], c_project_role.pk)

    def test_consultant_delete(self):
        consultant_role = FakeConsultantProjectRoleFactory.create(
            project=self.sprint.project_ptr,
            consultant=self.consultant,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )

        url = reverse(
            'api:relation:project:consultantprojectrole-detail',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': consultant_role.pk,
            },
        )
        self.client.login(username=self.super_user.email, password='123456')

        # DO ACTION
        self.client.delete(url, format='json')

        # ASSERTS
        self.assertEqual(
            ConsultantProjectRole.objects
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_COACH)
            .filter_by_project(self.sprint.project_ptr).count(),
            0
        )

    def test_consultant_not_delete(self):
        consultant_role = FakeConsultantProjectRoleFactory.create(
            project=self.sprint.project_ptr,
            consultant=self.consultant,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            status=settings.RELATION_ROLE_CH_ACTIVE,
        )
        FakeTeamFactory.create(
            project=self.sprint.project_ptr,
            coach=self.consultant,
        )

        url = reverse(
            'api:relation:project:consultantprojectrole-detail',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': consultant_role.pk,
            },
        )
        self.client.login(username=self.super_user.email, password='123456')

        # DO ACTION
        response = self.client.delete(url, format='json')

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertEqual(
            ConsultantProjectRole.objects
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_COACH)
            .filter_by_project(self.sprint.project_ptr).count(), 1)
