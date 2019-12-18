from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from exo_role.models import Category


class RolesAPITest(APITestCase):

    def test_get_roles(self):
        # PREPARE DATA
        url = reverse('api:roles')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(len(data), Category.objects.count())
