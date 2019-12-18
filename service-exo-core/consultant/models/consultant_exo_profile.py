from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from .contracting import ContractingData


class ConsultantExOProfile(TimeStampedModel):
    consultant = models.OneToOneField(
        'Consultant',
        related_name='exo_profile',
        blank=True, null=True,
        on_delete=models.CASCADE,
    )

    personal_mtp = models.TextField(blank=True, null=True)
    mtp_mastery = models.IntegerField(
        blank=True, null=True,
        choices=settings.CONSULTANT_SKILL_MTP_MASTERY_CHOICES,
    )

    availability = models.CharField(
        choices=settings.CONSULTANT_SKILL_AVAILABILITY,
        blank=True, null=True,
        max_length=1,
    )
    availability_hours = models.IntegerField(
        blank=True, null=True,
    )
    video_url = models.URLField(blank=True, null=True)

    _exo_activities = models.ManyToManyField(
        'exo_activity.ExOActivity',
        related_name='consultant_profiles',
        through='relation.ConsultantActivity',
    )

    def __str__(self):
        return '%s' % self.consultant

    def set_contracting(self, **kwargs):
        if kwargs:
            contracting, _ = ContractingData.objects.update_or_create(
                profile=self,
                defaults=kwargs,
            )
            return contracting

    def set_personal_mtp(self, value):
        self.personal_mtp = value
        self.save(update_fields=['personal_mtp', 'modified'])
