from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from test_utils.test_case_mixins import SuperUserTestMixin

from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from sprint_automated.models import SprintAutomated
from fastrack.faker_factories import FakeFastrackFactory
from utils.dates import increase_date, decrease_date

from ..conf import settings
from .test_mixins import TestProjectMixin


class ProjectFakerTest(TestProjectMixin, SuperUserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.project = self.create_project()
        self.create_superuser()

    def test_valid_create(self):
        self.assertIsNotNone(self.project.name)
        self.assertIsNotNone(self.project.customer)
        self.assertTrue(self.project.is_draft)
        self.assertIsNone(self.project.start)
        self.assertIsNone(self.project.end)

    def test_valid_dates(self):
        self.project.start = timezone.now()
        self.project.end = decrease_date(days=10)
        with self.assertRaises(ValidationError):
            self.project.full_clean()

    def test_project_status(self):
        waiting_project = self.create_project()
        self.assertTrue(waiting_project.is_draft)
        self.assertFalse(waiting_project.is_started)
        self.assertFalse(waiting_project.is_finished)
        self.assertEqual(
            waiting_project.status,
            settings.PROJECT_CH_PROJECT_STATUS_DRAFT,
        )

        started_project = self.create_project()
        started_project.set_started(self.super_user, start_date=timezone.now())
        self.assertTrue(started_project.is_started)
        self.assertFalse(started_project.is_waiting)
        self.assertFalse(started_project.is_finished)
        self.assertEqual(
            started_project.status,
            settings.PROJECT_CH_PROJECT_STATUS_STARTED,
        )

        ended_project = self.create_project(start=timezone.now())
        ended_project.set_finished(self.super_user, increase_date(days=10))
        self.assertTrue(ended_project.is_finished)
        self.assertFalse(ended_project.is_started)
        self.assertFalse(ended_project.is_waiting)
        self.assertEqual(
            ended_project.status,
            settings.PROJECT_CH_PROJECT_STATUS_FINISHED,
        )

    def test_project_real_type(self):

        self.assertEqual(self.project, self.project.real_type)

        sprint = FakeSprintAutomatedFactory()
        self.assertEqual(sprint, sprint.real_type)
        self.assertEqual(sprint, sprint.project_ptr.real_type)

    def test_project_type_project(self):

        self.assertEqual(self.project, self.project.real_type)

        sprint = FakeSprintAutomatedFactory()
        self.assertEqual(
            sprint.type_project.lower(),
            SprintAutomated._meta.model_name,
        )

    def test_project_is_type_property(self):

        project = self.create_project()
        self.assertFalse(project.is_sprint)

        sprint = FakeSprintAutomatedFactory()
        self.assertTrue(sprint.is_sprintautomated)

    def test_project_verbose_real_type(self):

        sprint = FakeSprintAutomatedFactory()
        self.assertEqual(
            sprint.project_ptr.type_verbose_name,
            sprint._meta.verbose_name,
        )

        fastrack = FakeFastrackFactory()
        self.assertEqual(
            fastrack.project_ptr.type_verbose_name,
            fastrack._meta.verbose_name,
        )
