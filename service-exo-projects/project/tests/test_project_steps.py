from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from utils.test_mixin import UserTestMixin

from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account
from ..signals_define import (
    project_started_changed,
    step_started_changed)


class ProjectStepTest(
        UserTestMixin,
        ProjectTestMixin,
        TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(
            created_by=cls.super_user,
            start=timezone.now().date())

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)
        self.project.refresh_from_db()

    def test_change_end(self):
        # PREPARE DATA
        previous_end = self.project.end
        last_step = self.project.steps.last()
        new_end = last_step.end + timedelta(days=10)

        # DO ACTION
        last_step.end = new_end
        last_step.save()

        # ASSERTS
        self.project.refresh_from_db()
        self.assertEqual(self.project.end, new_end)
        self.assertNotEqual(self.project.end, previous_end)

    def test_change_start(self):
        # PREPARE DATA
        previous_start = self.project.start
        previous_end = self.project.end
        first_step = self.project.steps.first()
        last_step = self.project.steps.last()
        new_start = previous_start + timedelta(days=10)
        new_end = previous_end + timedelta(days=10)

        # DO ACTION
        self.project.start = new_start
        self.project.save()
        project_started_changed.send(
            sender=self.project.__class__,
            instance=self.project)

        # ASSERTS
        self.project.refresh_from_db()
        first_step.refresh_from_db()
        last_step.refresh_from_db()
        self.assertEqual(self.project.end, new_end)
        self.assertEqual(self.project.start, new_start)
        self.assertEqual(first_step.start, new_start)
        self.assertEqual(last_step.end, new_end)
        self.assertNotEqual(self.project.end, previous_end)
        self.assertNotEqual(self.project.start, previous_start)

    def test_move_start(self):
        # PREPARE DATA
        step = self.project.steps.all()[5]
        previous_start = step.start
        new_start = previous_start + timedelta(days=10)

        previous_dates = [
            (_.start, _.end, _.index) for _ in self.project.steps.filter(index__gte=step.index)
        ]

        step.start = new_start
        step.save()

        # DO ACTION
        step_started_changed.send(
            sender=step.__class__,
            instance=step)

        # ASSERTS
        for start, end, index in previous_dates:
            step = self.project.steps.get(index=index)
            self.assertEqual(
                start + timedelta(days=10),
                step.start)
            self.assertEqual(
                end + timedelta(days=10),
                step.end)
