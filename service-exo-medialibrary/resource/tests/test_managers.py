from django.test import override_settings
from django.conf import settings
from django.utils import timezone

from rest_framework.test import APITestCase

from utils.test_case_mixins import UserTestMixin

from ..models import Resource, Tag, Category
from ..faker_factories import VideoFactory
from .mixins import TestResourceMixin


class TestManagersTestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def test_create_video_repeated(self):
        # PREPARE DATA
        video, video_created = self._create_video()

        # DO ACTION
        new_video, new_video_created = self._create_video(
            link=video.link,
            modified=timezone.now().isoformat())

        # ASSERTS
        self.assertTrue(video_created)
        self.assertFalse(new_video_created)
        self.assertEqual(Resource.objects.count(), 1)
        self.assertEqual(video.pk, new_video.pk)

    def test_create_tag_repeated(self):
        # PREPARE DATA
        tag = self._create_tag()

        # DO ACTION
        tag_new = self._create_tag(name=tag.name)

        # ASSERTS
        self.assertEqual(Tag.objects.count(), 1)
        self.assertEqual(tag.pk, tag_new.pk)

    def test_create_category_repeated(self):
        # PREPARE DATA
        category = self._create_category()

        # DO ACTION
        category_new = self._create_category(name=category.name)

        # ASSERTS
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(category.pk, category_new.pk)

    @override_settings(UPLOAD_REAL=False)
    def test_development_tag_in_resources(self):
        # PREPARE DATA
        num_videos = 10
        videos = VideoFactory.create_batch(size=num_videos)

        # DO ACTION
        self._create_resources(videos)

        # ASSERTS
        self.assertTrue(Resource.objects.exists())
        self.assertEqual(num_videos, Resource.objects.count())
        for resource in Resource.objects.all():
            self.assertIn(settings.RESOURCE_DEVELOPMENT_TAG_NAME,
                          resource.tags.all().values_list("name", flat=True))

    @override_settings(UPLOAD_REAL=True)
    def test_development_tag_in_resources_real(self):
        # PREPARE DATA
        num_videos = 10
        videos = VideoFactory.create_batch(size=num_videos)

        # DO ACTION
        self._create_resources(videos)

        # ASSERTS
        self.assertTrue(Resource.objects.exists())
        self.assertEqual(num_videos, Resource.objects.count())
        for resource in Resource.objects.all():
            self.assertNotIn(settings.RESOURCE_DEVELOPMENT_TAG_NAME,
                             resource.tags.all().values_list("name", flat=True))
