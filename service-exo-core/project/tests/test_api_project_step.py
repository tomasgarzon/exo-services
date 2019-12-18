from mock import patch

from django.urls import reverse
from django.conf import settings

from exo_role.models import ExORole

from utils.faker_factory import faker
from rest_framework import status
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from team.faker_factories import FakeTeamFactory
from test_utils import DjangoRestFrameworkTestCase
from team.models import TeamStep
from test_utils.mock_mixins import MagicMockMixin
from relation.helpers.consultant_project_enum import ConsultantProjectEnum
from relation.models import ConsultantProjectRole
from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory


class ProjectStepTestCase(
        SuperUserTestMixin,
        UserTestMixin,
        MagicMockMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_user()
        self.create_superuser()
        sprint = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        new_team = FakeTeamFactory.create(project=sprint.project_ptr)
        new_team.add_member(
            user_from=self.super_user,
            email=self.user.email,
            name=self.user.short_name,
        )
        consultant_manager_user = FakeUserFactory.create()
        consultant_for_manager_role = FakeConsultantFactory.create(
            user=consultant_manager_user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        self.manager_role = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=sprint.project_ptr,
            consultant=consultant_for_manager_role,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )
        self.team = new_team
        self.sprint = sprint
        self.step = sprint.project_ptr.steps.first()
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=self.sprint.project_ptr,
            consultant=FakeConsultantFactory.create(status=settings.CONSULTANT_STATUS_CH_ACTIVE),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )

    @patch.object(TeamStep, 'do_rating')
    @patch.object(TeamStep, 'do_feedback')
    def test_send_feedback(self, mock_do_feedback, mock_do_rating):
        # PREPARE DATA
        url = reverse(
            'api:project:step:step-feedback',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'team_id': self.team.id,
                'pk': self.step.id
            })
        data = {
            'rate': 3,
            'feedback': 2,
            'comments': faker.text()
        }

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_do_rating.called)
        self.assertEqual(
            self.get_mock_kwarg(mock_do_rating, 'user_from'),
            self.user)
        self.assertEqual(
            self.get_mock_kwarg(mock_do_rating, 'rating'),
            data['rate'])
        self.assertTrue(mock_do_feedback.called)
        self.assertEqual(
            self.get_mock_kwarg(mock_do_feedback, 'user_from'),
            self.user)
        self.assertEqual(
            self.get_mock_kwarg(mock_do_feedback, 'rating'),
            data['feedback'])
        self.assertEqual(
            self.get_mock_kwarg(mock_do_feedback, 'comment'),
            data['comments'])
        self.assertEqual(
            response.data['rate'], data['rate'])
        self.assertEqual(
            response.data['feedback'], data['feedback'])
        self.assertEqual(
            response.data['comments'], data['comments'])
        self.assertEqual(
            ConsultantProjectEnum(response.data['target']),
            ConsultantProjectEnum.COACH)

    def test_api_steps(self):
        # PREPARE DATA
        url = reverse(
            'api:project:step:step-list',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'team_id': self.team.id
            })

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        current_step = self.sprint.project_ptr.current_step()
        for data in response.data:
            if data['pk'] == current_step.id:
                self.assertTrue(data['current'])
            else:
                self.assertFalse(data['current'])

    def test_api_steps_wrong_team(self):
        # PREPARE DATA
        sprint = self.sprint
        another_team = FakeTeamFactory.create(project=sprint.project_ptr)
        url = reverse(
            'api:project:step:step-list',
            kwargs={
                'project_id': sprint.project_ptr.pk,
                'team_id': another_team.id
            })

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_api_step_detail(self):
        # PREPARE DATA
        url = reverse(
            'api:project:step:step-detail',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'team_id': self.team.id,
                'pk': self.sprint.project_ptr.steps.all()[3].pk,
            })

        # DO ACTION
        self.client.login(username=self.user.username, password='123456')
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_api_step_detail_fail(self):
        # PREPARE DATA
        sprint2 = FakeSprintAutomatedFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        team_ids = [self.team.id + 1, 200]
        step_ids = [sprint2.project_ptr.steps.all()[0].pk, 200]
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        for team_id in team_ids:
            for step_id in step_ids:
                url = reverse(
                    'api:project:step:step-detail',
                    kwargs={
                        'project_id': self.sprint.project_ptr.pk,
                        'team_id': team_id,
                        'pk': step_id,
                    })
                response = self.client.get(url)
                # ASSERTS
                self.assertTrue(response.status_code in [403, 404])
                self.assertTrue(status.is_client_error(response.status_code))
