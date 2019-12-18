from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class AssignmentAdvice(CreatedByMixin, TimeStampedModel):
    block = models.OneToOneField(
        'InformationBlock',
        related_name='assignment_advices',
        on_delete=models.CASCADE)

    def __str__(self):
        return self.block.title
