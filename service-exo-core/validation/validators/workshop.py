from django.db import DatabaseError
import logging

from .base import BaseValidator

from ..models import Validation
from . import (
    ParticipantPasswordValidator,
    TeamZoomValidator,
    ProjectInfoValidator,
    StepValidator,
)

logger = logging.getLogger('validator')


class WorkshopValidator(BaseValidator):

    def get_validations(self, project):
        validators = [
            ParticipantPasswordValidator,
            ProjectInfoValidator,
            TeamZoomValidator,
            StepValidator,
        ]
        return validators

    def validate(self):
        Validation.objects.clear_validations(self.project)
        validators = self.get_validations(self.project)

        for ValidatorClass in validators:
            validator = ValidatorClass(self.project)
            try:
                validator.validate()
            except DatabaseError as e:
                logger.info('Project#id: {} - Validator: {} - Error: {}'.format(
                    self.project.id,
                    validator,
                    e,
                ))
