from django.db import models

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin


class AssignmentText(CreatedByMixin, TimeStampedModel):
    block = models.OneToOneField(
        'InformationBlock',
        related_name='assignments_text',
        on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text
