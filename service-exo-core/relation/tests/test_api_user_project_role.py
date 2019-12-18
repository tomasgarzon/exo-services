from django.urls import reverse
from django.conf import settings

from rest_framework import status
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import (
    SuperUserTestMixin, UserTestMixin
)
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from invitation.models import Invitation
from utils.faker_factory import faker
from test_utils.mock_mixins import MagicMockMixin

from ..faker_factories import FakeUserProjectRoleFactory
from ..models import UserProjectRole


class UserProjectRoleTest(
        UserTestMixin,
        SuperUserTestMixin,
        MagicMockMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create(
            user=self.user)
        self.sprint = FakeSprintAutomatedFactory.create(
            created_by=self.user)

    def test_add_member_customer(self):
        # PREPARE DATA
        url = reverse(
            'api:relation:project:userprojectrole-list',
            kwargs={'project_id': self.sprint.project_ptr.pk},
        )
        data = {
            'name': faker.name(),
            'email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        }
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.sprint.project_ptr.users_roles.filter(user__email=data['email']).count(), 1)
        role = UserProjectRole.objects.filter(
            project=self.sprint.project_ptr,
            user__email=data['email']).first()
        self.assertEqual(Invitation.objects.filter_by_object(role).count(), 1)
        invitation = Invitation.objects.filter_by_object(role)[0]
        self.assertTrue(invitation.is_pending)
        self.assertTrue(role.is_inactive)

    def test_add_member_no_customer(self):
        # PREPARE DATA
        url = reverse(
            'api:relation:project:userprojectrole-list',
            kwargs={'project_id': self.sprint.project_ptr.pk},
        )
        data = {
            'name': '{} {}'.format(faker.first_name(), faker.last_name()),
            'email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        }
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.sprint.project_ptr.users_roles.filter(user__email=data['email']).count(), 1)
        role = UserProjectRole.objects.filter(
            project=self.sprint.project_ptr,
            user__email=data['email']).first()
        self.assertEqual(Invitation.objects.filter_by_object(role).count(), 1)
        invitation = Invitation.objects.filter_by_object(role)[0]
        self.assertTrue(invitation.is_pending)
        self.assertTrue(role.is_inactive)
        self.assertEqual(role.user.short_name, data['name'].split(' ')[0])
        self.assertEqual(role.user.full_name, data['name'])

    def test_members_in_project(self):
        # PREPARE DATA
        FakeUserProjectRoleFactory.create_batch(
            size=3,
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_INACTIVE,
        )
        url = reverse(
            'api:relation:project:userprojectrole-list',
            kwargs={'project_id': self.sprint.project_ptr.pk},
        )
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 3)

    def test_user_delete(self):
        # PREPARE DATA
        user_role = FakeUserProjectRoleFactory.create(
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_INACTIVE,
        )
        url = reverse(
            'api:relation:project:userprojectrole-detail',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': user_role.pk,
            },
        )
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        self.client.delete(url, format='json')

        # ASSERTS
        self.assertEqual(
            UserProjectRole.objects.all().count(), 0)

    def test_add_member_duplicated(self):
        # PREPARE DATA
        url = reverse(
            'api:relation:project:userprojectrole-list',
            kwargs={'project_id': self.sprint.project_ptr.pk},
        )
        data = {
            'name': faker.name(),
            'email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        }
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        for k in range(3):
            response = self.client.post(url, data=data, format='json')
            self.assertTrue(status.is_success(response.status_code))

        # ASSERTS
        self.assertEqual(
            self.sprint.project_ptr.users_roles.filter(user__email=data['email']).count(), 1)
        role = UserProjectRole.objects.filter(
            project=self.sprint.project_ptr,
            user__email=data['email']).first()
        self.assertEqual(Invitation.objects.filter_by_object(role).count(), 1)
        invitation = Invitation.objects.filter_by_object(role)[0]
        self.assertTrue(invitation.is_pending)
        self.assertTrue(role.is_inactive)

    def test_update_member(self):
        # PREPARE DATA
        user_role = FakeUserProjectRoleFactory.create(
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_INACTIVE,
        )
        url = reverse(
            'api:relation:project:userprojectrole-detail',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': user_role.pk},
        )
        data = {
            'name': faker.name(),
            'email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        }
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.sprint.project_ptr.users_roles.filter(user__email=data['email']).count(), 1)
        self.assertEqual(
            self.sprint.project_ptr.users_roles.all().count(), 1)
        self.assertEqual(
            response.data['email'],
            self.sprint.project_ptr.users_roles.all().first().user.email)

    def test_update_member_existing_email(self):
        # PREPARE DATA
        user = FakeUserFactory.create()

        user_role = FakeUserProjectRoleFactory.create(
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_INACTIVE,
        )
        url = reverse(
            'api:relation:project:userprojectrole-detail',
            kwargs={
                'project_id': self.sprint.project_ptr.pk,
                'pk': user_role.pk},
        )
        data = {
            'name': faker.name(),
            'email': user.email,
            'role': settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
        }
        self.client.login(username=self.user.email, password='123456')

        # DO ACTION
        response = self.client.put(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.sprint.project_ptr.users_roles.filter(user__email=data['email']).count(), 1)
        self.assertEqual(
            self.sprint.project_ptr.users_roles.all().count(), 1)
        self.assertEqual(
            self.sprint.project_ptr.users_roles.all().first().user,
            user)
        self.assertEqual(
            response.data['email'],
            self.sprint.project_ptr.users_roles.all().first().user.email)

    def test_add_exo_staff_but_not_superuser(self):
        # PREPARE DATA
        self.client.login(username=self.user.email, password='123456')

        url = reverse('api:relation:project:userprojectrole-list', kwargs={
            'project_id': self.sprint.project_ptr.pk,
        })
        data = {
            'name': faker.name(),
            'email': faker.email(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_OTHER,
        }

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

        # PREPARE DATA
        data['email'] = self.super_user.email

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
