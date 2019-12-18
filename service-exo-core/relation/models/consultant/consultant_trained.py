from django.db import models

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin


class ConsultantTrained(
        CreatedByMixin,
        TimeStampedModel
):
    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='trained_sessions',
        on_delete=models.CASCADE,
    )
    training_session = models.ForeignKey(
        'learning.TrainingSession',
        related_name='attendants',
        on_delete=models.CASCADE,
    )
