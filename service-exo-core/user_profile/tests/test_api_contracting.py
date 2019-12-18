from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker
from consultant.models import ContractingData


class UserProfileContractingAPITests(
        SuperUserTestMixin, DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_superuser()

    def test_change_contracting(self):
        consultant = FakeConsultantFactory.create()
        ContractingData.objects.create(
            profile=consultant.exo_profile,
            name=faker.name(),
            address=faker.address(),
            company_name=faker.company(),
        )
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        url = reverse(
            'api:profile:change-contracting',
            kwargs={'pk': consultant.user.pk},
        )
        data = {
            'name': faker.name(),
            'address': faker.address(),
            'company_name': faker.company(),
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(
            consultant.exo_profile.contracting_data.name, data['name'],
        )
        self.assertEqual(ContractingData.objects.count(), 1)

    def test_create_contracting(self):
        consultant = FakeConsultantFactory.create()
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        url = reverse(
            'api:profile:change-contracting',
            kwargs={'pk': consultant.user.pk},
        )
        data = {
            'name': faker.name(),
            'company_name': '',
        }
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(
            consultant.exo_profile.contracting_data.name, data['name'],
        )
        self.assertEqual(ContractingData.objects.count(), 1)
