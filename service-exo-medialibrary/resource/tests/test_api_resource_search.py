from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_case_mixins import UserTestMixin

from .mixins import TestResourceMixin
from ..conf import settings


class TestResourceSearchAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_get_videos_search_filter(self):
        # PREPARE DATA
        video, _ = self._create_video()
        url = reverse("api:resources:library-list")
        data = {
            'search': video.name,
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED,
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get("results")), 1)
