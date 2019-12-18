from datetime import timedelta

from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from utils.test_case_mixins import UserTestMixin

from ..faker_factories import VideoFactory
from ..conf import settings
from .mixins import TestResourceMixin


class TestOrderingAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_ordering_by_name_ascendent(self):
        # PREPARE DATA
        name_A = "A"
        name_B = "B"
        video_A = VideoFactory.create(name=name_A)
        video_B = VideoFactory.create(name=name_B)
        videos = [video_A, video_B]
        self._create_resources(videos)
        url = reverse("api:resources:library-list")
        data = {
            'page': 1,
            'ordering': 'name',
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get("results")[0]['name'], name_A)

    def test_ordering_by_name_descendent(self):
        # PREPARE DATA
        name_A = "A"
        name_B = "B"
        video_A = VideoFactory.create(name=name_A)
        video_B = VideoFactory.create(name=name_B)
        videos = [video_A, video_B]
        self._create_resources(videos)
        url = reverse("api:resources:library-list")
        data = {
            'page': 1,
            'ordering': '-name',
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get("results")[0]['name'], name_B)

    def test_ordering_by_modified_time_ascendent(self):
        # PREPARE DATA
        created_time_A = timezone.now().isoformat()
        created_time_B = (timezone.now() + timedelta(days=1)).isoformat()
        video_A = VideoFactory.create(modified_time=created_time_A)
        video_B = VideoFactory.create(modified_time=created_time_B)
        videos = [video_A, video_B]
        self._create_resources(videos)
        url = reverse("api:resources:library-list")
        data = {
            'page': 1,
            'ordering': 'modified',
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        result0 = parse_datetime(response.data.get("results")[0]['modified'])
        result1 = parse_datetime(response.data.get("results")[1]['modified'])
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(result0 < result1)

    def test_ordering_by_modified_time_descendent(self):
        # PREPARE DATA
        created_time_A = timezone.now().isoformat()
        created_time_B = (timezone.now() + timedelta(days=1)).isoformat()
        video_A = VideoFactory.create(modified_time=created_time_A)
        video_B = VideoFactory.create(modified_time=created_time_B)
        videos = [video_A, video_B]
        self._create_resources(videos)
        url = reverse("api:resources:library-list")
        data = {
            'page': 1,
            'ordering': '-modified',
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED
        }

        # DO ACTION
        response = self.client.get(url, data=data)
        result0 = parse_datetime(response.data.get("results")[0]['modified'])
        result1 = parse_datetime(response.data.get("results")[1]['modified'])
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(result0 > result1)
