from django.db import models

from model_utils.models import TimeStampedModel
from ...managers.consultant_exo_area import ConsultantExOAreaManager


class ConsultantExOArea(
        TimeStampedModel
):
    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='exo_areas',
        on_delete=models.CASCADE,
    )
    exo_area = models.ForeignKey(
        'exo_area.ExOArea',
        related_name='consultants',
        on_delete=models.CASCADE,
    )
    comment = models.TextField(blank=True, null=True)

    objects = ConsultantExOAreaManager()

    def __str__(self):
        return '{} - {}'.format(self.consultant, self.exo_area)
