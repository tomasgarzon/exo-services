from django.urls import reverse
from django.test import TestCase
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
        url = reverse('api:ecosystem:members')

        # DO ACTION
        self.client.login(
            username=self.super_user.username,
            password='123456'
        )
        response = self.client.get(url)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 24)
        self.assertEqual(len(data.get('results')), 15)

    def test_api_get_all_members(self):
        # PREPARE DATA
        params = {'status': 'all'}
        url = reverse('api:ecosystem:members')

        # DO ACTION
        self.client.login(
            username=self.super_user.username,
            password='123456'
        )
        response = self.client.get(url, data=params)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 24)
        self.assertEqual(len(data.get('results')), 15)

    def test_api_filter_by_location(self):
        # PREPARE DATA
        params = {'location': 'Germany'}
        url = reverse('api:ecosystem:members')

        # DO ACTION
        self.client.login(
            username=self.user.username,
            password='123456'
        )
        response = self.client.get(url, data=params)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 3)
        self.assertEqual(len(data.get('results')), 3)

    def test_api_search(self):
        # PREPARE DATA
        params = {'search': 'tokyo'}
        url = reverse('api:ecosystem:members')

        # DO ACTION
        self.client.login(
            username=self.user.username,
            password='123456'
        )
        response = self.client.get(url, data=params)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 1)
        self.assertEqual(len(data.get('results')), 1)

    def test_api_order_by_projects(self):
        # PREPARE DATA
        parms = {'sort': '-projects'}
        url = reverse('api:ecosystem:members')

        # DO ACTION
        self.client.login(
            username=self.user.username,
            password='123456'
        )
        response = self.client.get(url, data=parms)

        # ASSERTS
        data = response.json()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(data.get('count'), 24)
