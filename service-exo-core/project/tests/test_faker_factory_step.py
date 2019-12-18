from django.test import TestCase

from ..faker_factories import FakeStepFactory
from ..conf import settings


class ProjectFakerTest(TestCase):

    def setUp(self):
        super().setUp()

    def test_valid_create(self):
        new_step = FakeStepFactory()
        self.assertIsNotNone(new_step.project)
        self.assertIsNotNone(new_step.name)
        self.assertIsNotNone(new_step.index)
        self.assertIsNone(new_step.start)
        self.assertIsNone(new_step.end)
        self.assertEqual(new_step.status, settings.PROJECT_STEP_STATUS_DEFAULT)
        self.assertTrue(new_step.project.steps.count())
