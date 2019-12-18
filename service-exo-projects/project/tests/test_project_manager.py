from django.test import TestCase
from django.conf import settings

from utils.test_mixin import UserTestMixin

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class ProjectManagerTest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def test_order_by_status(self):
        # PREPARE DATA
        statuses = [
            settings.PROJECT_CH_STATUS_WAITING,
            settings.PROJECT_CH_STATUS_FINISHED,
            settings.PROJECT_CH_STATUS_DRAFT,
            settings.PROJECT_CH_STATUS_STARTED,
            settings.PROJECT_CH_STATUS_REMOVED,
        ]
        for status in statuses:
            FakeProjectFactory.create(
                created_by=self.super_user,
                status=status)

        # DO ACTION
        queryset = models.Project.objects.all().annotate_status_order().order_by('status_order')

        # ASSERTS
        status_expected = [status for status, _ in settings.PROJECT_CH_STATUS]

        for index, status in enumerate(status_expected):
            self.assertEqual(queryset[index].status, status)
