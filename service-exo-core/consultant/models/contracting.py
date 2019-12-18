from django.db import models

from model_utils.models import TimeStampedModel


class ContractingData(TimeStampedModel):
    profile = models.OneToOneField(
        'ConsultantExOProfile',
        null=True, blank=True,
        related_name='contracting_data',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        blank=True, null=True,
        max_length=200,
    )
    tax_id = models.CharField(
        max_length=30,
        blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    company_name = models.CharField(
        blank=True, null=True,
        max_length=200,
    )

    def __str__(self):
        return '{}, {} {}'.format(self.name, self.address, self.company_name)

    @property
    def consultant(self):
        return self.profile.consultant
