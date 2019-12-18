from django.urls import reverse
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin


class TestIntercomUser(
    UserTestMixin,
    DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()

    def test_intercom_hash_for_user(self):
        # PREPARE DATA
        self.client.login(username=self.user.email, password='123456')
        settings.INTERCOM_SECRET_KEY = '1234'

        # DO ACTION
        response = self.client.get(reverse('api:accounts:me'))

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('intercom_hash', response.data[0])
        self.assertEqual(
            self.user.intercom_hash,
            response.data[0].get('intercom_hash'),
        )
        self.assertEqual(
            self.user.build_intercom_hash(),
            self.user.get_intercom_hash_from_redis(),
        )
