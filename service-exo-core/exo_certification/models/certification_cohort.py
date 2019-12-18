import uuid

from django.conf import settings
from django.db import models

from model_utils.models import TimeStampedModel


class CertificationCohort(TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    date = models.DateTimeField()
    language = models.CharField(
        max_length=3,
        choices=settings.EXO_CERTIFICATION_COHORT_CH_LANGS,
        default=settings.EXO_CERTIFICATION_COHORT_LANG_CH_DEFAULT,
    )
    seats = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    first_price_tier = models.FloatField(default=0)
    currency = models.CharField(
        max_length=4,
        choices=settings.EXO_CERTIFICATION_CURRENCY_CH_CURRENCIES,
        default=settings.EXO_CERTIFICATION_CURRENCY_CH_DEFAULT,
    )
    invoice_concept = models.CharField(max_length=255)
    status = models.CharField(
        max_length=1,
        choices=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_STATUSES,
        default=settings.EXO_CERTIFICATION_COHORT_STATUS_CH_DEFAULT,
    )
    certification = models.ForeignKey(
        'ExOCertification',
        null=True,
        blank=False,
        related_name='cohorts',
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(
        'project.Project',
        null=True,
        blank=True,
        related_name='certification_cohort',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Certification Cohort'
        verbose_name_plural = 'Certification Cohorts'

    def __str__(self):
        return '{} ({})'.format(
            self.title,
            self.date,
        )

    @property
    def title(self):
        return '[{}] {} {}'.format(
            self.certification.get_level_display(),
            self.certification.name,
            self.language,
        )

    @property
    def level(self):
        return self.certification.level
