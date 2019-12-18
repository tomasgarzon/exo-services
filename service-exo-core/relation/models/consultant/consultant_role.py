from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin


class ConsultantRole(CreatedByMixin, TimeStampedModel):
    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='consultant_roles',
        on_delete=models.CASCADE,
    )

    certification_role = models.ForeignKey(
        'exo_role.CertificationRole',
        related_name='consultants_certified',
        on_delete=models.CASCADE,
        blank=True, null=True,
    )
    certification_group = models.ForeignKey(
        'ConsultantRoleCertificationGroup',
        related_name='consultant_roles',
        blank=True, null=True,
        on_delete=models.CASCADE,
    )
    credentials = GenericRelation(
        'certification.CertificationCredential',
        related_query_name='consultant_roles')

    def __str__(self):
        return '{} {}'.format(self.consultant, self.certification_role)

    @property
    def user(self):
        return self.consultant.user
