import random

from django.urls import reverse
from django.conf import settings

from rest_framework import status

from customer.faker_factories import FakeCustomerFactory
from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.faker_factory import faker

from ..models import GenericProject


class TestAPICreateGenericProject(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()

    def test_api_create_generic_project(self):
        # PREPARE DATA
        url = reverse('api:project:create-service')
        customer = FakeCustomerFactory.create()
        duration = random.randint(1, 100)
        data = {
            'type_project': settings.PROJECT_CH_TYPE_GENERIC_PROJECT,
            'name': faker.name(),
            'duration': duration,
            'lapse': settings.PROJECT_LAPSE_PERIOD,
            'customer': customer.id,
        }
        self.client.login(username=self.super_user.username, password='123456')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        generic_project = GenericProject.objects.get(id=response.data.get('id'))
        self.assertEqual(generic_project.name, data.get('name'))
        self.assertEqual(generic_project.duration, duration)
        self.assertEqual(generic_project.lapse, settings.PROJECT_LAPSE_PERIOD)
        self.assertEqual(generic_project.customer.pk, customer.pk)
        self.assertEqual(generic_project.settings.version, settings.PROJECT_CH_VERSION_2)
