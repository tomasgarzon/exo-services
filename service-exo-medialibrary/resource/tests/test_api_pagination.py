from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from utils.test_case_mixins import UserTestMixin
from utils.pagination import PAGE_SIZE

from ..conf import settings
from .mixins import TestResourceMixin


class TestPaginationAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_pagination_default(self):
        # PREPARE DATA
        num_videos = 50
        url = reverse("api:resources:library-list")
        data = {
            'page': 1,
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED,
        }
        self._create_videos(num_videos)

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get("results")), PAGE_SIZE)

    def test_page_size_query_param(self):
        # PREPARE DATA
        num_videos = 50
        page_size = 20
        url = reverse("api:resources:library-list")
        data = {
            'page': 1,
            'page_size': page_size,
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED,
        }
        self._create_videos(num_videos)

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get("results")), page_size)
