from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_case_mixins import UserTestMixin

from ..conf import settings
from .mixins import TestResourceMixin


class TestResourceAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_get_resources(self):
        # PREPARE DATA
        num_videos = 10
        url = reverse("api:resources:library-list")
        self._create_videos(num_videos)
        data = {
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(num_videos, len(response.data.get("results")))

    def test_get_resources_with_camel_case_keys(self):
        # PREPARE DATA
        num_videos = 10
        url = reverse("api:resources:library-list")
        self._create_videos(num_videos)
        data = {
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        for result in response.data.get("results"):
            for key in result.keys():
                self.assertFalse(key.find(' ') != -1)

    def test_delete_resource(self):
        # PREPARE DATA
        video, _ = self._create_video()
        url = reverse('api:resources:library-detail', kwargs={'pk': video.pk})
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.delete(url, data={})
        video.refresh_from_db()

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(video.status, settings.RESOURCE_CH_STATUS_REMOVED)

    def test_delete_resource_no_exists(self):
        # PREPARE DATA
        url = reverse('api:resources:library-detail', kwargs={'pk': 1234})
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.delete(url, data={})

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
