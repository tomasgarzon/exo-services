from django.db import models

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin


class AssignmentAdviceItem(CreatedByMixin, TimeStampedModel):
    assignment_advice = models.ForeignKey(
        'AssignmentAdvice', related_name='assignment_advice_items',
        on_delete=models.CASCADE)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.description
