from django.urls import reverse
from django.conf import settings
from django.test import TestCase

from rest_framework import status

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin


class TestAPIAccountMeUser(
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()

    def test_get_account_me(self):
        # PREPARE DATA
        url = reverse('api:accounts:me')
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_get_account_by_uuid(self):
        # PREPARE DATA
        url = reverse(
            'api:accounts:me-uuid', kwargs={'uuid': self.user.uuid.__str__()})

        # DO ACTION
        response = self.client.get(url, HTTP_USERNAME=settings.AUTH_SECRET_KEY)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
