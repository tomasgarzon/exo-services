from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from test_utils.test_case_mixins import UserTestMixin


class TestCertsAPITestCase(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    def test_api_certifications_list(self):
        # PREPARE DATA
        url = reverse('api:certifications:list')
        self.client.login(username=self.user.username, password='123456')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.json()),
            3,
        )
