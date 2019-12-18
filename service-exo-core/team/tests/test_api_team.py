from django.urls import reverse
from django.conf import settings

from mock import patch
from rest_framework import status

from exo_role.models import ExORole

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from utils.faker_factory import faker
from sprint_automated.faker_factories import FakeSprintAutomatedFactory

from ..models import Team


class TestAPITeam(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.sprint = FakeSprintAutomatedFactory.create()
        self.super_user.set_password('123456')
        self.super_user.save()

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_api_create_no_members(self, task_handler):
        coaches = FakeConsultantFactory.create_batch(
            size=3, user__is_active=True,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )
        for coach in coaches:
            ConsultantProjectRole.objects.get_or_create_consultant(
                user_from=self.super_user,
                consultant=coach,
                project=self.sprint.project_ptr,
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            )
        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:project:team:create', kwargs={'project_id': self.sprint.project_ptr.pk})
        data = {
            'name': faker.first_name(),
            'stream': 'S',
            'zoom_id': faker.word(),
            'coach': coaches[0].pk,
            'team_members': [],
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.filter(project=self.sprint.project_ptr).count(), 1)

    def create_team_api(self):
        coaches = FakeConsultantFactory.create_batch(
            size=4, user__is_active=True,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )
        for coach in coaches:
            ConsultantProjectRole.objects.get_or_create_consultant(
                user_from=self.super_user,
                consultant=coach,
                project=self.sprint.project_ptr,
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            )

        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:project:team:create', kwargs={'project_id': self.sprint.project_ptr.pk})
        members = []

        for k in range(5):
            name = faker.word()
            email = faker.email()
            members.append({'short_name': name, 'email': email})

        data = {
            'name': faker.first_name(),
            'stream': 'S',
            'zoom_id': faker.word(),
            'coach': coaches[0].pk,
            'team_members': members,
        }

        response = self.client.post(url, data=data, format='json')
        return response, coaches

    def test_api_create_with_data(self):
        response, _ = self.create_team_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.filter(project=self.sprint.project_ptr).count(), 1)
        team = Team.objects.filter(project=self.sprint.project_ptr)[0]
        self.assertEqual(team.team_members.count(), 5)

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_api_get_team(self, task_handler):
        response, coaches = self.create_team_api()
        self.client.login(username=self.super_user.username, password='123456')
        team = Team.objects.filter(project=self.sprint.project_ptr)[0]
        slug = team.slug
        url = reverse(
            'api:project:team:edit', kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': team.pk,
            },
        )
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['team_members']), 5)
        team_members = []
        team_members.append(response.data['team_members'][0])
        team_members.append(response.data['team_members'][1])
        team_members.append({
                            'short_name': faker.first_name(),
                            'email': faker.email(),
                            })
        new_name = faker.word()
        new_coach = coaches[1]
        data = {
            'name': new_name,
            'stream': response.data['stream'],
            'coach': new_coach.pk,
            'zoom_id': faker.word(),
            'team_members': team_members,
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(team.coach, new_coach)
        self.assertEqual(len(response.data['team_members']), 3)
        self.assertEqual(team.name, new_name)
        self.assertNotEqual(team.slug, slug)

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_zoom_id_meetings(self, task_handler):
        response, coaches = self.create_team_api()

        zoom_id = faker.word()
        data = {
            'name': response.data.get('name'),
            'stream': response.data.get('stream'),
            'coach': response.data.get('coach'),
            'zoom_id': zoom_id,
            'team_members': response.data.get('team_members'),
        }

        self.client.login(username=self.super_user.username, password='123456')
        team = Team.objects.filter(project=self.sprint.project_ptr)[0]

        url = reverse(
            'api:project:team:edit', kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': team.pk,
            },
        )

        response = self.client.put(url, data=data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('zoom_id'), zoom_id)

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_assert_async_task_called(self, task_handler):
        response, coaches = self.create_team_api()
        task_handler.assert_called()

    @patch('zoom_project.tasks.UpdateZoomRoomTask.apply_async')
    def test_api_edit_team(self, task_handler):
        # edit a team changing the coach to team members
        self.sprint.project_ptr.launch(self.super_user)
        coaches = FakeConsultantFactory.create_batch(
            size=4, user__is_active=True,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )
        for coach in coaches:
            ConsultantProjectRole.objects.get_or_create_consultant(
                user_from=self.super_user,
                consultant=coach,
                project=self.sprint.project_ptr,
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            )
        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:project:team:create', kwargs={'project_id': self.sprint.project_ptr.pk})
        members = []
        for k in range(2):
            name = faker.word()
            email = faker.email()
            members.append({'short_name': name, 'email': email})
        for k in coaches[1:]:
            members.append({
                'short_name': k.user.short_name,
                'email': k.user.email,
            })
        data = {
            'name': faker.first_name(),
            'stream': 'S',
            'zoom_id': faker.word(),
            'coach': coaches[0].pk,
            'team_members': members,
        }
        response = self.client.post(url, data=data, format='json')
        team = Team.objects.filter(project=self.sprint.project_ptr)[0]
        url = reverse(
            'api:project:team:edit', kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': team.pk,
            },
        )
        members.append({
            'short_name': coaches[0].user.short_name,
            'email': coaches[0].user.email,
        })
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        team.refresh_from_db()
        self.assertEqual(
            Team.objects.filter_by_project(
                self.sprint.project_ptr,
            ).filter_by_user(
                self.sprint.project_ptr, coaches[0].user,
            ).count(), 1,
        )
        data['coach'] = coaches[1].pk
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Team.objects.filter_by_project(
                self.sprint.project_ptr,
            ).filter_by_user(
                self.sprint.project_ptr, coaches[0].user,
            ).count(), 1,
        )
