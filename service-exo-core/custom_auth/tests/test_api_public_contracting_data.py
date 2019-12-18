from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker
from consultant.faker_factories import FakeConsultantFactory
from consultant.models import ContractingData


class ContactingDataTest(DjangoRestFrameworkTestCase):

    def test_contracting_data_ok_empty(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user__password='123456')
        data = {'username': consultant.user.email, 'password': '123456'}
        url = reverse('api:accounts:public-contracting-data')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(
            data.get('contractingData'),
            {'name': '', 'taxId': '', 'address': '', 'companyName': ''}
        )

    def test_contracting_data_wrong_user(self):
        # PREPARE DATA
        data = {'username': faker.email(), 'password': '123456'}
        url = reverse('api:accounts:public-contracting-data')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_contracting_data_ok_filled(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(user__password='123456')
        contracting_data = ContractingData.objects.create(
            profile=consultant.exo_profile,
            name=faker.name(),
            address=faker.address(),
            company_name=faker.company(),
        )
        data = {'username': consultant.user.email, 'password': '123456'}
        url = reverse('api:accounts:public-contracting-data')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data['fullName'], consultant.user.full_name)
        self.assertEqual(data['contractingData']['name'], contracting_data.name)
