from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker

from .mixins import TestResourceMixin
from ..faker_factories import FakeResourceFactory


class TestResourceEditAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.do_login(self.user)

    def test_edit_resource_with_no_tags(self):
        # PREPARE DATA
        video = FakeResourceFactory.create()
        url = reverse('api:resources:library-detail', kwargs={'pk': video.pk})
        new_name = faker.word()
        new_description = faker.text()
        data = {
            'name': new_name,
            'description': new_description,
            'tags': []
        }
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_resource_with_tags_and_no_permissions(self):
        # PREPARE DATA
        video = FakeResourceFactory.create()
        tag = self._create_tag(commit=True)
        tags = [tag.pk]
        url = reverse('api:resources:library-detail', kwargs={'pk': video.pk})
        new_name = faker.word()
        new_description = faker.text()
        data = {
            'name': new_name,
            'description': new_description,
            'tags': tags
        }

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_resource_with_tags_and_permissions(self):
        # PREPARE DATA
        video = FakeResourceFactory.create()
        tag = self._create_tag(commit=True)
        tags = [tag.pk]
        url = reverse('api:resources:library-detail', kwargs={'pk': video.pk})
        new_name = faker.word()
        new_description = faker.text()
        data = {
            'name': new_name,
            'description': new_description,
            'tags': tags
        }
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.put(url, data=data)
        video.refresh_from_db()

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(video.name, new_name)
        self.assertEqual(video.description, new_description)
        self.assertTrue(self._exists_tag_in_last_resource(tag.pk))

    def test_edit_resource_url(self):
        # PREPARE DATA
        video = FakeResourceFactory.create()
        tag = self._create_tag(commit=True)
        tags = [tag.pk]
        url = reverse('api:resources:library-detail', kwargs={'pk': video.pk})
        old_video_url = video.url
        data = {
            'name': faker.word(),
            'description': faker.text(),
            'url': faker.url(),
            'tags': tags
        }
        self._add_permissions_for_library_to_user()

        # DO ACTION
        response = self.client.put(url, data=data)
        video.refresh_from_db()

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(old_video_url, video.url)
        self.assertTrue(self._exists_tag_in_last_resource(tag.pk))
