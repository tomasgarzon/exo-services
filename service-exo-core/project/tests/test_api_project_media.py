from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from rest_framework import status

from test_utils.test_case_mixins import SuperUserTestMixin

from .test_mixins import TestProjectMixin


class ProjectMediaTest(TestProjectMixin, SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.project = self.create_project()
        self.client.login(username=self.super_user.username, password='123456')

    def test_valid_create(self):
        # PREPARE DATA
        url = reverse('project:project:populate-media', kwargs={'project_id': self.project.pk})

        for _type, _ in settings.PROJECT_CH_TYPE_PROJECT:

            # DO ACTION
            response = self.client.post(url, data={'_type': _type})

            # ASSERTS
            self.assertTrue(status.is_redirect(response.status_code))
