from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin

from ...conf import settings


class ConsultantRoleCertificationGroup(
        CreatedByMixin,
        TimeStampedModel):

    name = models.CharField(max_length=255)
    description = models.TextField()
    issued_on = models.DateField(blank=True, null=True)
    _type = models.CharField(
        max_length=100,
        choices=settings.RELATION_CONSULTANT_ROLE_GROUP_TYPE_CHOICES)
    certification_groups = GenericRelation(
        'certification.CertificationGroup',
        related_query_name='consultant_role_group')

    def __str__(self):
        return '{}: {} - {}'.format(self.name, self.description, self._type)

    @property
    def accredible_group(self):
        return self.certification_groups.first()
