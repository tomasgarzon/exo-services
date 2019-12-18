from django.apps import apps
from django.conf import settings

from project.models import Step

from .base import BaseValidator


class SprintAutomatedFeedbacksValidator(BaseValidator):

    def validate(self):
        pending = False
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_SPRINT_AUTOMATED_FEEDBACKS,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': settings.VALIDATION_LABEL_VALIDATION[
                    settings.VALIDATION_CH_SPRINT_AUTOMATED_FEEDBACKS
                ],
            },
        )

        StepStream = apps.get_model(app_label='project', model_name='StepStream')
        steps_with_feedbacks = Step.objects.filter_by_project(self.project).filter_by_index_range(
            start=settings.SPRINT_AUTOMATED_STEP_INDEX_FEEDBACK_START,
            end=settings.SPRINT_AUTOMATED_STEP_INDEX_FEEDBACK_END)
        streams = StepStream.objects.filter(step__in=steps_with_feedbacks)

        for stream in streams:
            for feedback in stream.typeform_feedback.all():
                if not feedback.typeform_url:
                    pending = True

        validation.pending() if pending else validation.fixed()
        return validation.is_pending
