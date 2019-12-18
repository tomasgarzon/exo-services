from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_case_mixins import UserTestMixin

from .mixins import TestResourceMixin


class TestTagAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_get_tags_from_library(self):
        # PREPARE DATA
        num_tags = 10
        url = reverse("api:resources:tag-list")
        self._create_tags(num_tags)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(num_tags, len(response.data))
