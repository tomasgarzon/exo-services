from ..conf import settings
from .base import BaseValidator


class ProjectManagerValidator(BaseValidator):

    def validate(self):
        subject = ''
        for code, label in self.project.customize['roles']['labels']:
            if code in self.project.customize['roles'].get('manager'):
                subject = settings.VALIDATION_LABEL_VALIDATION[
                    settings.VALIDATION_CH_NO_MANAGER
                ].format(label)

        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_NO_MANAGER,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': subject,
            },
        )
        if self.project.project_manager:
            validation.fixed()
        else:
            validation.pending()
        return validation.is_pending
