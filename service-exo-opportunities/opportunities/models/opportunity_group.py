import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings

from model_utils.models import TimeStampedModel

from ..origin_helper import get_project_info, get_exo_project_info


class OpportunityGroup(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4)
    origin = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_CH_GROUP_ORIGIN)
    related_uuid = models.UUIDField()
    total = models.IntegerField()
    exo_role = models.ForeignKey(
        'exo_role.ExORole',
        on_delete=models.SET_NULL,
        blank=True, null=True)
    certification_required = models.ForeignKey(
        'exo_role.CertificationRole',
        on_delete=models.SET_NULL,
        blank=True, null=True)
    entity = models.CharField(
        max_length=200,
        blank=True, null=True,
        default=None,
    )
    duration_unity = models.CharField(
        max_length=1,
        blank=True, null=True,
        choices=settings.OPPORTUNITIES_DURATION_UNITY_CHOICES,
    )
    duration_value = models.IntegerField(blank=True, null=True)
    managers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='manager_groups')
    budgets = JSONField(blank=True, null=True)

    @property
    def consumed(self):
        return self.opportunities.not_draft().not_removed().aggregate(
            total=models.Sum('num_positions')).get('total', 0) or 0

    def has_positions_availables(self, total, previous_opp=None):
        if total <= 0:
            return True
        if previous_opp is None:
            total_used = self.consumed
            return total_used + total <= self.total
        else:
            total_used = self.opportunities.exclude(
                pk=previous_opp.pk).not_draft().not_removed().aggregate(
                    total=models.Sum('num_positions')).get('total', 0) or 0
            return total_used + total <= self.total

    @property
    def info_detail(self):
        if self.origin == settings.OPPORTUNITIES_CH_GROUP_TEAM:
            response = get_project_info(self.related_uuid)
        else:
            response = get_exo_project_info(self.related_uuid)
        try:
            return response[0]['name']
        except Exception:
            return ''

    @property
    def advisor_request_section(self):
        if self.origin == settings.OPPORTUNITIES_CH_GROUP_TEAM:
            response = get_project_info(self.related_uuid)
        else:
            response = get_exo_project_info(self.related_uuid)
        try:
            return response[0]['advisorURL']
        except Exception:
            return ''
