from django.urls import reverse

from rest_framework import status

from exo_role.models import CertificationRole

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory

from ..models import ConsultantRole
from ..faker_factories import FakeConsultantRoleFactory


class ConsultantRoleTest(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create()
        self.certification_role = CertificationRole.objects.all().first()

    def test_api_create(self):
        # PREPARE DATA
        self.client.login(username=self.super_user.email, password='123456')
        url = reverse('api:relation:consultant-role-list', kwargs={'consultant_pk': self.consultant.pk})
        data = {
            'certification_role': self.certification_role.id,
            'consultant': self.consultant.id,
        }

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        consultant_role = ConsultantRole.objects.get(consultant=self.consultant)
        self.assertIsNotNone(consultant_role.created_by)
        self.assertIsNotNone(consultant_role.certification_role)

    def test_api_get(self):
        # PREPARE DATA
        FakeConsultantRoleFactory.create_batch(
            size=3,
            consultant=self.consultant,
        )
        self.client.login(username=self.super_user.email, password='123456')
        url = reverse('api:relation:consultant-role-list', kwargs={'consultant_pk': self.consultant.pk})

        # DO ACTION
        response = self.client.get(url, format='json')

        # ASSERTS
        self.assertEqual(len(response.data), 3)
        self.assertEqual(self.consultant.certification_roles.count(), 3)

    def test_api_delete(self):
        # PREPARE DATA
        consultant_role = FakeConsultantRoleFactory.create(
            consultant=self.consultant,
        )
        self.client.login(username=self.super_user.email, password='123456')
        url = reverse(
            'api:relation:consultant-role-detail',
            kwargs={
                'consultant_pk': self.consultant.pk,
                'pk': consultant_role.pk,
            },
        )

        # DO ACTION
        self.client.delete(url, format='json')

        # ASSERTS
        self.assertEqual(ConsultantRole.objects.filter(id=consultant_role.pk).count(), 0)
