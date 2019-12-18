from django.test import TestCase, override_settings
from django.utils import timezone
from django.conf import settings

from mock import patch

from ..clients import VimeoClient
from ..models import Resource, Category, Tag
from ..faker_factories import (
    VideoFactory, TagFactory, CategoryFactory)
from .mixins import TestResourceMixin


class TestVimeoAPITestCase(TestResourceMixin, TestCase):

    def setUp(self):
        self.client = VimeoClient()

    @patch('resource.clients.vimeo.VimeoClient.get_videos_paginated')
    def test_get_vimeo_videos(self, mock_videos):
        # PREPARE DATA
        num_videos = 10
        mock_videos.return_value = VideoFactory.create_batch(size=num_videos)
        videos = self.client.get_videos_paginated()

        # DO ACTION
        self._create_resources(videos)

        # ASSERTS
        self.assertTrue(mock_videos.called)
        self.assertTrue(Resource.objects.exists())
        self.assertEqual(len(videos), num_videos)
        self.assertEqual(Resource.objects.count(), num_videos)

    @patch('resource.clients.vimeo.VimeoClient.get_videos_paginated')
    def test_get_vimeo_videos_after_changes(self, mock_get_videos_paginated):
        # PREPARE DATA
        num_videos = 10
        mock_get_videos_paginated.return_value = VideoFactory.create_batch(size=num_videos)
        videos = self.client.get_videos_paginated()
        self._create_resources(videos)

        # DO ACTION
        videos[0]['modified_time'] = timezone.now().isoformat()
        self._create_resources(videos)

        # ASSERTS
        self.assertTrue(Resource.objects.exists())

    @patch('resource.clients.vimeo.VimeoClient.get_categories')
    def test_get_vimeo_categories(self, mock_categories):
        # PREPARE DATA
        num_categories = 5
        mock_categories.return_value = CategoryFactory.create_batch(size=num_categories)
        categories = self.client.get_categories()

        # DO ACTION
        Category.objects.create_categories_vimeo(categories)

        # ASSERTS
        self.assertTrue(mock_categories.called)
        self.assertTrue(Category.objects.exists())
        self.assertEqual(len(categories), Category.objects.count())

    @override_settings(UPLOAD_REAL=False)
    @patch('resource.clients.vimeo.VimeoClient.get_video_tags')
    def test_get_vimeo_video_tags(self, mock_tags):
        # PREPARE DATA
        num_tags = 5
        video, _ = self._create_video()
        mock_tags.return_value = TagFactory.create_batch(size=num_tags)
        tags = self.client.get_video_tags(video.id)

        # DO ACTION
        Tag.objects.create_tags_vimeo(tags)

        # ASSERTS
        self.assertTrue(mock_tags.called)
        self.assertTrue(Tag.objects.exists())
        self.assertEqual(len(tags) + settings.RESOURCE_DEVELOPMENT_TAGS_COUNT, Tag.objects.count())

    @patch('resource.clients.vimeo.VimeoClient.get_video_categories')
    def test_get_vimeo_video_categories(self, mock_categories):
        # PREPARE DATA
        num_categories = 5
        video, _ = self._create_video()
        mock_categories.return_value = CategoryFactory.create_batch(size=num_categories)
        categories = self.client.get_video_categories(video.id)

        # DO ACTION
        Category.objects.create_categories_vimeo(categories)

        # ASSERTS
        self.assertTrue(mock_categories.called)
        self.assertTrue(Category.objects.exists())
        self.assertEqual(len(categories), Category.objects.count())
