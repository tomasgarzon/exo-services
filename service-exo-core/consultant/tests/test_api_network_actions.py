from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import tag
from django.contrib.auth.models import Permission
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin
from team.faker_factories import FakeTeamFactory

from ..faker_factories import FakeConsultantFactory
from ..models import Consultant


User = get_user_model()


@tag('sequencial')
class TestAPIConsultantActions(
        UserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()
        perm = Permission.objects.get(codename=settings.CONSULTANT_PERMS_CONSULTANT_LIST_AND_EXPORT)
        self.user.user_permissions.add(perm)
        self.consultant = FakeConsultantFactory.create()

    def test_can_delete(self):
        user_id = self.consultant.user.id
        self.client.login(
            username=self.user.email, password='123456',
        )
        url = reverse('api:consultant:delete', args=[self.consultant.pk])
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data['status'], 'deleted')
        self.assertEqual(Consultant.all_objects.filter(id=self.consultant.id).count(), 0)
        self.assertEqual(User.objects.filter(id=user_id).count(), 0)

    def test_can_not_delete(self):
        FakeTeamFactory.create(coach=self.consultant)
        self.client.login(
            username=self.user.email, password='123456',
        )
        url = reverse('api:consultant:delete', args=[self.consultant.pk])
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data['status'], 'not-deleted')
        self.assertEqual(Consultant.all_objects.filter(id=self.consultant.id).count(), 1)
