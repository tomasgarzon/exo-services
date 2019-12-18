from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from utils.faker_factory import faker
from utils.test_case_mixins import UserTestMixin

from .mixins import TestResourceMixin
from ..faker_factories import FakeResourceFactory
from ..models import Resource
from ..conf import settings


class TestResourceWithProjectsAPITestCase(UserTestMixin, TestResourceMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        self.do_token_login()

    def test_add_uuid_from_resource_projects(self):
        # PREPARE DATA
        uuid_project = faker.uuid4()
        resource = FakeResourceFactory.create()
        url = reverse("api:resources:library-add-to-projects", kwargs={'pk': resource.pk})

        # DO ACTION
        response = self.client.put(url, data={'uuid': uuid_project})
        resource.refresh_from_db()
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(uuid_project in response.data.get('projects'))
        self.assertTrue(resource.projects)

    def test_remove_uuid_from_resource_projects(self):
        # PREPARE DATA
        uuid_project = faker.uuid4()
        resource = FakeResourceFactory.create(projects=uuid_project)
        url = reverse("api:resources:library-remove-from-projects", kwargs={'pk': resource.pk})

        # DO ACTION
        response = self.client.put(url, data={'uuid': uuid_project})
        resource.refresh_from_db()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(uuid_project not in response.data.get('projects'))
        self.assertFalse(resource.projects)

    def test_assign_resources_post_save_project(self):
        # PREPARE DATA
        self.do_token_login()
        sections = list(settings.RESOURCE_CH_SECTIONS)
        project_types = list(settings.RESOURCE_CH_TYPE_PROJECT)

        for section_type, section_name in sections:
            FakeResourceFactory.create(sections=section_type)

        for project_type, project_name in project_types:
            new_project_uuid = faker.uuid4()
            data = {
                'uuid': new_project_uuid,
                'type_project_lower': project_name
            }
            url_api = reverse('api:resources:post-save-project')

            # DO ACTION
            response = self.client.post(url_api, data=data)

            # ASSERTS
            self.assertTrue(status.is_success(response.status_code))
            resource = Resource.objects.filter_by_section(
                settings.RESOURCE_RELATION_TYPES_AND_SECTIONS[project_type]).get()
            self.assertTrue(new_project_uuid in resource.project_list)
