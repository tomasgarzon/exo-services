from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_case_mixins import UserTestMixin

from .mixins import TestResourceMixin


class TestCategoryAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()

    def test_get_categories_from_library(self):
        # PREPARE DATA
        num_categories = 10
        url = reverse("api:resources:category-list")

        self.do_login(self.user)
        self._create_categories(num_categories)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(num_categories, len(response.data))
