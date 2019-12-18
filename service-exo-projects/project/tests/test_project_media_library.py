import re

from django.test import TestCase
from django.conf import settings

import requests_mock

from utils.test_mixin import UserTestMixin

from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class MediaLibraryProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_media_library_call(self, mock_request):
        # PREPARE DATA
        url_for_media_library = '{}{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.MEDIA_LIBRARY_HOST,
            'api/resources/post-save-project/')
        handler = mock_request.register_uri(
            'POST',
            re.compile(url_for_media_library),
            json={})

        # DO ACTION
        with self.settings(POPULATOR_MODE=False):
            project = FakeProjectFactory.create(created_by=self.super_user)
            self.assertTrue(handler.called)
            data = handler.request_history[0].json()
            self.assertEqual(data['uuid'], project.uuid.__str__())
            self.assertEqual(data['type_project_lower'], 'sprintautomated')
