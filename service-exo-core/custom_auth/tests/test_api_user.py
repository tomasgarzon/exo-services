from django.conf import settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from account_config.models import ConfigParam
from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from consultant.models import Consultant, ContractingData


class UserAPITest(
        UserTestMixin,
        SuperUserTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def test_notifiable_consultants(self):
        # PREPARE DATA
        consultants = FakeConsultantFactory.create_batch(
            size=16,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        for consultant in consultants:
            consultant.user.add_django_permission(
                settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL,
            )
        param = ConfigParam.objects.get(name='new_open_opportunity')
        param.set_value_for_agent(consultants[0], False)
        param.set_value_for_agent(consultants[1], False)
        param.set_value_for_agent(consultants[1], True)
        param.set_value_for_agent(consultants[1], False)
        param.set_value_for_agent(consultants[2], True)
        self.consultants_not_active = consultants[0:2]
        consultant_not_activated = consultants[3]
        param.set_value_for_agent(consultant_not_activated, True)
        user = consultant_not_activated.user
        user.is_active = False
        user.save()

        url = reverse('api:accounts:user-can-receive-opportunities')

        # DO ACTION
        response = self.client.get(url, HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(data), 13)
        param = ConfigParam.objects.get(
            name='new_open_opportunity')
        emails_not_active = [d.user.email for d in self.consultants_not_active]
        for result in data:
            consultant = Consultant.objects.get(
                user__email=result['email'])
            self.assertTrue(param.get_value_for_agent(consultant))
            self.assertFalse(result['email'] in emails_not_active)

    def test_contracting_data(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        ContractingData.objects.create(
            profile=consultant.exo_profile,
            name=faker.name(),
            address=faker.address(),
            company_name=faker.company(),
        )
        url = reverse(
            'api:accounts:user-contracting-data',
            kwargs={'uuid': consultant.user.uuid.__str__()})

        # DO ACTION
        response = self.client.get(url, HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(data['name'])

    def test_contracting_data_not_exist(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        url = reverse(
            'api:accounts:user-contracting-data',
            kwargs={'uuid': consultant.user.uuid.__str__()})

        # DO ACTION
        response = self.client.get(url, HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(consultant.exo_profile.contracting_data)

    def test_edit_contracting_data(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        contracting_data = ContractingData.objects.create(
            profile=consultant.exo_profile,
            name=faker.name(),
            address=faker.address(),
            company_name=faker.company(),
        )
        url = reverse(
            'api:accounts:user-contracting-data',
            kwargs={'uuid': consultant.user.uuid.__str__()})

        new_data = {
            'name': faker.name(),
            'address': faker.address(),
            'company_name': faker.company(),
            'tax_id': '2522',
        }

        # DO ACTION
        response = self.client.put(
            url,
            format='json',
            data=new_data, HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        # ASSERTS
        contracting_data.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(contracting_data.name, new_data['name'])
