
from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class ExOCertification(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    level = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        choices=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVELS,
        default=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_DEFAULT,
    )
    certification_role = models.ForeignKey(
        'exo_role.CertificationRole',
        related_name='certifications',
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'ExO Certification'
        verbose_name_plural = 'ExO Certifications'

    def __str__(self):
        return '[{}] {}'.format(
            self.level,
            self.name,
        )
