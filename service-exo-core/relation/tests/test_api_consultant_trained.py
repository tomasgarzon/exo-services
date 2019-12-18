from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from learning.faker_factories import FakeTrainingSessionFactory

from ..models import ConsultantTrained
from ..faker_factories import FakeConsultantTrainedFactory


class ConsultantTrainedTest(
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_superuser()
        self.consultant = FakeConsultantFactory.create()
        self.training_session = FakeTrainingSessionFactory.create()

    def test_api_create(self):
        self.client.login(username=self.super_user.email, password='123456')
        url = reverse('api:relation:consultant-trained-list', kwargs={'consultant_pk': self.consultant.pk})
        data = {
            'training_session': self.training_session.id,
            'consultant': self.consultant.id,
        }
        response = self.client.post(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        trained = ConsultantTrained.objects.get(consultant=self.consultant)
        self.assertIsNotNone(trained.created_by)
        self.assertIsNotNone(trained.training_session)

    def test_api_get(self):
        FakeConsultantTrainedFactory.create_batch(
            size=3,
            consultant=self.consultant,
        )
        self.client.login(username=self.super_user.email, password='123456')
        url = reverse('api:relation:consultant-trained-list', kwargs={'consultant_pk': self.consultant.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(len(response.data), 3)
