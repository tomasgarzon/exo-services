from django.db import models

from model_utils.models import TimeStampedModel

from ..managers.bulk_creation_consultant import BulkCreationConsultantManager


class BulkCreationConsultant(TimeStampedModel):
    SUCCESS_MESSAGE = 'Success'
    ERROR_MESSAGE = 'Error'

    consultant = models.ForeignKey(
        'Consultant',
        blank=True, null=True,
        on_delete=models.CASCADE,
    )
    bulk_creation = models.ForeignKey(
        'BulkCreation',
        related_name='consultants',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        blank=True,
        null=True, max_length=200,
    )
    email = models.EmailField(
        blank=True,
        null=True,
    )
    coins = models.IntegerField(
        blank=True, null=True,
    )
    status = models.CharField(
        max_length=10,
        default=SUCCESS_MESSAGE,
    )
    error_message = models.CharField(
        max_length=100,
    )

    objects = BulkCreationConsultantManager()

    def set_error(self, message):
        self.status = self.ERROR_MESSAGE
        self.error_message = message
        self.save()

    def set_error_email_used(self):
        self.set_error('The email account has already being used')

    def set_error_achievement_created(self):
        self.set_error('This user already has coins')

    def set_error_missing_information(self):
        self.set_error('Missing name or email')

    def set_consultant(self, consultant):
        self.consultant = consultant
        self.save(update_fields=['consultant', 'modified'])

    @property
    def is_success(self):
        return self.status == self.SUCCESS_MESSAGE
