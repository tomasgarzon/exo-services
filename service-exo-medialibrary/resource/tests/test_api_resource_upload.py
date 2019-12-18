from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from mock import patch

from utils.test_case_mixins import UserTestMixin

from .mixins import TestResourceMixin
from ..faker_factories import VideoUploadFactory
from ..conf import settings


class TestUploadVideoAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    @patch('resource.models.Resource.upload_video_async')
    def test_upload_resource_from_public_urls_providers_with_no_tags(self, mock_upload_resource):
        # PREPARE DATA
        url_api = reverse('api:resources:library-list')
        urls_public = [
            "https://www.youtube.com/watch?v=GPB8ovFD_W4"
            "https://vimeo.com/4413241"
        ]
        self._add_permissions_for_library_to_user()

        # DO ACTION
        for url_public in urls_public:
            video_data = VideoUploadFactory.create(url=url_public, tags=[])
            response = self.client.post(url_api, data=video_data)

            # ASSERTS
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertFalse(mock_upload_resource.called)

    @patch('resource.models.Resource.upload_video_async')
    def test_upload_resource_from_public_urls_providers_with_no_permissions(self, mock_upload_resource):
        # PREPARE DATA
        url_api = reverse('api:resources:library-list')
        urls_public = [
            "https://www.youtube.com/watch?v=GPB8ovFD_W4",
            "https://vimeo.com/4413241"
        ]
        tag = self._create_tag(commit=True)
        tags = [tag.pk]

        # DO ACTION
        for url_public in urls_public:
            video_data = VideoUploadFactory.create(url=url_public, tags=tags)
            response = self.client.post(url_api, data=video_data)

            # ASSERTS
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertFalse(mock_upload_resource.called)

    @patch('resource.models.Resource.upload_video_async')
    def test_upload_resource_from_public_urls_providers_with_tags_and_permissions(self, mock_upload_resource):
        # PREPARE DATA
        url_api = reverse('api:resources:library-list')
        urls_public = [
            "https://www.youtube.com/watch?v=GPB8ovFD_W4",
            "https://vimeo.com/4413241"
        ]
        tag = self._create_tag(commit=True)
        tags = [tag.pk]
        self._add_permissions_for_library_to_user()

        # DO ACTION
        for url_public in urls_public:
            video_data = VideoUploadFactory.create(url=url_public, tags=tags)
            response = self.client.post(url_api, data=video_data)

            # ASSERTS
            self.assertTrue(mock_upload_resource.called)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data.get("name"), video_data.get("name"))
            self.assertEqual(response.data.get("description"), video_data.get("description"))
            self.assertEqual(response.data.get("status"), settings.RESOURCE_CH_STATUS_DRAFT)
            self.assertIsNone(response.data.get("link"))
            self.assertFalse(response.data.get("internal"))
            self.assertTrue(self._exists_tag_in_last_resource(tag.pk))

    @patch('resource.models.Resource.upload_video_async')
    def test_upload_video_dropbox_with_tags_and_permissions(self, mock_upload_resource):
        # PREPARE DATA
        url = "https://www.dropbox.com/s/o6dnqzyhar647qu/gatos.mp4?dl=0"
        url_api = reverse('api:resources:library-list')
        tag = self._create_tag(commit=True)
        tags = [tag.pk]
        video_data = VideoUploadFactory.create(tags=tags, url=url)
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.post(url_api, data=video_data)

        # ASSERTS
        self.assertTrue(mock_upload_resource.called)
        self.assertEqual(response.data.get("name"), video_data.get("name"))
        self.assertEqual(response.data.get("description"), video_data.get("description"))
        self.assertEqual(response.data.get("status"), settings.RESOURCE_CH_STATUS_DRAFT)
        self.assertTrue(response.data.get("internal"))
        self.assertEqual(self._get_last_resource().url, url)
        self.assertTrue(self._exists_tag_in_last_resource(tag.pk))

    @patch('resource.models.Resource.upload_video_async')
    def test_upload_video_drive_with_tags_and_permissions(self, mock_upload_resource):
        # PREPARE DATA
        url = "https://drive.google.com/open?id=1sIBAPpK6S4QerSlS8efIscci5whF6ppX"
        url_api = reverse('api:resources:library-list')
        tag = self._create_tag(commit=True)
        tags = [tag.pk]
        video_data = VideoUploadFactory.create(tags=tags, url=url)
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.post(url_api, data=video_data)

        # ASSERTS
        self.assertTrue(mock_upload_resource.called)
        self.assertEqual(response.data.get("name"), video_data.get("name"))
        self.assertEqual(response.data.get("description"), video_data.get("description"))
        self.assertEqual(response.data.get("status"), settings.RESOURCE_CH_STATUS_DRAFT)
        self.assertTrue(response.data.get("internal"))
        self.assertEqual(self._get_last_resource().url, url)
        self.assertTrue(self._exists_tag_in_last_resource(tag.pk))
