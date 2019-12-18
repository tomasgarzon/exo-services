from django.db import DatabaseError
import logging

from .base import BaseValidator
from . import (
    TeamValidator, ParticipantPasswordValidator,
    TeamZoomValidator,
    CreationDateValidator,
    ProjectManagerValidator,
    ProjectInfoValidator,
    PlatformCreateValidator,
    SprintAutomatedStartDateValidator,
    StepValidator,
)
from ..models import Validation


logger = logging.getLogger('validator')


class ProjectValidator(BaseValidator):

    def get_validations(self, project):
        validators = [
            TeamValidator,
            ParticipantPasswordValidator,
            CreationDateValidator,
            ProjectManagerValidator,
            ProjectInfoValidator,
            TeamZoomValidator,
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


class FastrackValidator(ProjectValidator):
    def get_validations(self, project):
        validators = [
            PlatformCreateValidator,
            TeamValidator,
            TeamZoomValidator,
            ParticipantPasswordValidator,
            ProjectManagerValidator,
            SprintAutomatedStartDateValidator,
            StepValidator,
        ]

        return validators
