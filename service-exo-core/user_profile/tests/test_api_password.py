from django.urls import reverse

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from utils.faker_factory import faker


class UserProfilePasswordAPITests(SuperUserTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        self.create_superuser()

    def test_change_password_ok(self):
        consultant = FakeConsultantFactory.create()
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        url = reverse('api:profile:change-password', kwargs={'pk': consultant.user.pk})
        data = {}
        password = '.12dd345678'
        data['new_password'] = password
        data['re_new_password'] = password
        response = self.client.put(url, data=data, format='json')
        consultant.user.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(consultant.user.check_password(password))

    def test_change_password(self):
        consultant = FakeConsultantFactory.create()
        self.client.login(
            username=self.super_user.username,
            password='123456',
        )
        url = reverse('api:profile:change-password', kwargs={'pk': consultant.user.pk})
        data = {'new_password': faker.password(), 're_new_password': faker.password()}
        response = self.client.put(url, data=data, format='json')
        self.assertTrue(status.is_client_error(response.status_code))
        self.assertIsNotNone(response.data.get('non_field_errors'))
