from django.db import models

from model_utils.models import TimeStampedModel

from ...conf import settings
from ...managers.consultant_exo_attribute import ConsultantExOAttributeManager


class ConsultantExOAttribute(TimeStampedModel):

    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='exo_attributes',
        on_delete=models.CASCADE,
    )
    exo_attribute = models.ForeignKey(
        'exo_attributes.ExOAttribute',
        related_name='consultants',
        on_delete=models.CASCADE,
    )
    level = models.IntegerField(
        choices=settings.RELATION_EXO_ATTRIBUTE_CHOICES,
        default=settings.RELATION_EXO_ATTRIBUTE_DEFAULT,
    )

    objects = ConsultantExOAttributeManager()

    def __str__(self):
        return '{} - {}: {}'.format(
            self.consultant,
            self.exo_attribute,
            self.get_level_display(),
        )
