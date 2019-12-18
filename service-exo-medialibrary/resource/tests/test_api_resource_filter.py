from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.test_case_mixins import UserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeResourceFactory
from ..conf import settings
from .mixins import TestResourceMixin


class TestResourceFiltersAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        self.create_user()
        self.create_super_user()
        self.do_login(self.user)

    def _prepare_data(self):
        self._create_videos(5)
        video, _ = self._create_video()
        return video

    def test_get_videos_filter_by_name(self):
        # PREPARE DATA
        video = self._prepare_data()
        url = reverse("api:resources:library-list")
        data = {
            'name': video.name,
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED,
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get("results")), 1)

    def test_get_videos_filter_by_tag(self):
        # PREPARE DATA
        video = self._prepare_data()
        tag = self._create_tag()
        tag2 = self._create_tag()
        url = reverse("api:resources:library-list")
        self._add_tags_to_resource([tag], video)
        tags_filter = "{},{}".format(tag.name, tag2.name)
        data = {
            'tags': tags_filter,
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED,
        }

        # DO ACTION
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data.get("results")), 1)

    def test_resource_filter_by_sections(self):
        # PREPARE DATA
        size = 10
        url = reverse("api:resources:library-list")
        FakeResourceFactory.create_batch(
            size=size,
            status=settings.RESOURCE_CH_STATUS_AVAILABLE,
            sections=settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED)

        # DO ACTION
        response = self.client.get(url, data={
            'sections': settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('count'), size)

    def test_resource_filter_by_sections_with_empty_values(self):
        # PREPARE DATA
        size = 5
        url = reverse("api:resources:library-list")

        FakeResourceFactory.create_batch(
            size=size,
            status=settings.RESOURCE_CH_STATUS_AVAILABLE,
            sections=settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED)
        sections = '{},,{},'.format(settings.RESOURCE_CH_SECTION_SPRINT_AUTOMATED,
                                    settings.RESOURCE_CH_SECTION_TRAINERS)

        # DO ACTION
        response = self.client.get(url, data={
            'sections': sections})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('count'), size)

    def test_resource_filter_by_sections_empty_with_superuser(self):
        # PREPARE DATA
        url = reverse("api:resources:library-list")
        self.do_login(self.super_user)

        # DO ACTION
        response = self.client.get(url, data={'sections': ''})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    def test_resource_filter_by_sections_empty_with_not_superuser(self):
        # PREPARE DATA
        url = reverse("api:resources:library-list")

        # DO ACTION
        response = self.client.get(url, data={'sections': ''})

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_resource_filter_by_projects(self):
        # PREPARE DATA
        size_with_uuid = 10
        size_without_uuid = 5
        uuid_project = faker.uuid4()
        url = reverse("api:resources:library-project-list")
        FakeResourceFactory.create_batch(
            size=size_with_uuid,
            status=settings.RESOURCE_CH_STATUS_AVAILABLE,
            projects=str(uuid_project))
        FakeResourceFactory.create_batch(
            size=size_without_uuid,
            status=settings.RESOURCE_CH_STATUS_AVAILABLE,
            projects='')
        self.do_token_login()

        # DO ACTION
        response = self.client.get(url, data={'projects': uuid_project})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('count'), size_with_uuid)

    def test_resource_filter_by_projects_empty_with_not_superuser(self):
        # PREPARE DATA
        url = reverse("api:resources:library-project-list")

        # DO ACTION
        response = self.client.get(url, data={'projects': ''})

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
