import logging

from django.db import DatabaseError

from .base import BaseValidator
from . import (
    TeamValidator,
    TeamZoomValidator,
    CreationDateValidator,
    ProjectManagerValidator,
    ProjectStartValidator,
)
from ..models import Validation


logger = logging.getLogger('validator')


class GenericProjectValidator(BaseValidator):

    def get_validations(self, project):
        return [
            TeamValidator,
            TeamZoomValidator,
            CreationDateValidator,
            ProjectManagerValidator,
            ProjectStartValidator,
        ]

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
