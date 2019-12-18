from assignment.models import AssignmentStep
from project.models import Step

from ..conf import settings
from .base import BaseValidator


class AssignmentForStepsValidator(BaseValidator):

    def validate(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_ASSIGNMENT_STEP,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': settings.VALIDATION_LABEL_VALIDATION[settings.VALIDATION_CH_ASSIGNMENT_STEP],
            }
        )

        steps = Step.objects.filter_by_project(self.project)

        for step in steps:
            assignments_related_to_step = AssignmentStep.objects.filter_by_step(step)

            if not assignments_related_to_step.exists():
                validation.pending()
                break
            else:
                validation.fixed()

        return validation.is_pending
