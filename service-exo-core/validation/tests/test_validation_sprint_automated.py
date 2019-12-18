from django import test
from django.conf import settings
from django.utils import timezone

from project.models import Step, StepStream
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from learning.faker_factories import FakeMicroLearningFactory
from typeform_feedback.models import GenericTypeformFeedback
from utils.faker_factory import faker

from ..validators import (
    TeamValidator,
    TeamZoomValidator,
    CreationDateValidator,
    ParticipantPasswordValidator,
    ProjectManagerValidator,
    SprintAutomatedStartDateValidator,
    SprintAutomatedFeedbacksValidator,
    SprintAutomatedMicrolearningsValidator,
)
from ..validators.sprint_automated import SprintAutomatedValidator


class SprintAutomatedValidatorTest(SuperUserTestMixin, test.TestCase):

    def setUp(self):
        self.create_superuser()

    def prepare_data(self):
        self.sprint_automated = FakeSprintAutomatedFactory.create()
        self.project = self.sprint_automated.project_ptr

    def test_validation_sprint_automated(self):
        # PREPARE DATA
        self.prepare_data()
        validator = SprintAutomatedValidator(self.project)

        # DO ACTION
        validator.validate()

        # ASSERTS
        self.assertEqual(self.project.validations.count(), 6)

        self.assertEqual(self.project.validations.filter_by_status_pending().count(), 5)

    def test_validator_sprint_automated(self):
        # PREPARE DATA
        self.prepare_data()
        validator = SprintAutomatedValidator(self.project)
        inputs = validator.get_validations(self.project)
        outputs = [
            TeamValidator,
            TeamZoomValidator,
            CreationDateValidator,
            ParticipantPasswordValidator,
            ProjectManagerValidator,
            SprintAutomatedStartDateValidator,
            SprintAutomatedMicrolearningsValidator,
            SprintAutomatedFeedbacksValidator
        ]

        # ASSERTS
        for index, validation in enumerate(inputs):
            self.assertEqual(validation.__name__, outputs[index].__name__)

    def test_validation_sprint_automated_start_date_validator(self):
        # PREPARE DATA
        self.prepare_data()
        steps = Step.objects.filter_by_project(self.project)
        validator = SprintAutomatedStartDateValidator(self.project)
        is_pending_validation = validator.validate()

        # ASSERTS
        self.assertTrue(is_pending_validation)

        # DO ACTION
        for step in steps:
            step.start = timezone.now()
            step.save()

        # ASSERTS
        is_pending_validation = validator.validate()
        self.assertFalse(is_pending_validation)

    def test_validation_sprint_automated_feedbacks_validator(self):
        # PREPARE DATA
        self.prepare_data()
        steps_with_feedbacks = Step.objects.filter_by_project(self.project).filter_by_index_range(
            start=settings.SPRINT_AUTOMATED_STEP_INDEX_FEEDBACK_START,
            end=settings.SPRINT_AUTOMATED_STEP_INDEX_FEEDBACK_END)
        streams = StepStream.objects.filter(step__in=steps_with_feedbacks)
        feedbacks_list_id = streams.values_list('typeform_feedback', flat=True)
        feedbacks = GenericTypeformFeedback.objects.filter(id__in=feedbacks_list_id)
        validator = SprintAutomatedFeedbacksValidator(self.project)

        # DO ACTION
        for feedback in feedbacks:
            feedback.url = faker.url()
            feedback.save()

        # ASSERTS
        is_pending_validation = validator.validate()
        self.assertFalse(is_pending_validation)

    def test_validation_sprint_automated_microlearnings_validator(self):
        # PREPARE DATA
        self.prepare_data()
        steps_with_microlearnings = Step.objects.filter_by_project(self.project).filter_by_index_range(
            start=settings.SPRINT_AUTOMATED_STEP_INDEX_MICROLEARNING_START,
            end=settings.SPRINT_AUTOMATED_STEP_INDEX_MICROLEARNING_END)
        streams = StepStream.objects.filter(step__in=steps_with_microlearnings)
        validator = SprintAutomatedMicrolearningsValidator(self.project)

        # DO ACTION
        for stream in streams.filter(microlearning__isnull=True):
            FakeMicroLearningFactory.create(step_stream=stream)

        # ASSERTS
        is_pending_validation = validator.validate()
        self.assertFalse(is_pending_validation)
