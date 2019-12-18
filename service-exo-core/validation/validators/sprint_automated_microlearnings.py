from django.apps import apps

from project.models import Step

from ..conf import settings
from .base import BaseValidator


class SprintAutomatedMicrolearningsValidator(BaseValidator):

    def validate(self):
        pending = False
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_SPRINT_AUTOMATED_MICROLEARNINGS,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': settings.VALIDATION_LABEL_VALIDATION[
                    settings.VALIDATION_CH_SPRINT_AUTOMATED_MICROLEARNINGS
                ],
            },
        )
        StepStream = apps.get_model(app_label='project', model_name='StepStream')
        steps_with_microlearnings = Step.objects.filter_by_project(self.project).filter_by_index_range(
            start=settings.SPRINT_AUTOMATED_STEP_INDEX_MICROLEARNING_START,
            end=settings.SPRINT_AUTOMATED_STEP_INDEX_MICROLEARNING_END)
        streams = StepStream.objects.filter(step__in=steps_with_microlearnings)

        for stream in streams:
            if not stream.has_microlearning():
                pending = True

        validation.pending() if pending else validation.fixed()
        return validation.is_pending
