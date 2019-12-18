
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin

from .mixins import EcosystemAPITestMixin


class TestEcosystemAPITestCase(
        EcosystemAPITestMixin,
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.initialize_consultants()

    def test_api_default(self):
        # PREPARE DATA
        url = reverse('api:ecosystem-public:members')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 7)
        self.assertEqual(len(data.get('results')), 7)

    def test_api_search_location(self):
        # PREPARE DATA
        params = {'search': 'tokyo'}
        url = reverse('api:ecosystem-public:members')

        # DO ACTION
        response = self.client.get(url, data=params)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(len(data.get('results')), 1)

    def test_api_search_certification(self):
        # PREPARE DATA
        params = {'search': 'coach'}
        url = reverse('api:ecosystem-public:members')

        # DO ACTION
        response = self.client.get(url, data=params)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 3)
        self.assertEqual(len(data.get('results')), 3)
