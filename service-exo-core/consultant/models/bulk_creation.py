from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin
from ..managers.bulk_creation import BulkCreationManager


class BulkCreation(CreatedByMixin, TimeStampedModel):

    _consultants = models.ManyToManyField(
        'Consultant',
        related_name='bulks',
        through='BulkCreationConsultant',
        blank=True,
    )
    file_csv = models.FileField(
        'Upload the csv file',
        upload_to='bulk_creation_consultant',
        null=True,
    )
    objects = BulkCreationManager()

    def __str__(self):
        return str(self.file_csv)
