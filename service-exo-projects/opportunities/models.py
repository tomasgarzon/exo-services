from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel

from .conf import settings


class OpportunityProjectRole(TimeStampedModel):
    user_project_role = models.OneToOneField(
        'project.UserProjectRole',
        related_name='opportunity_related',
        on_delete=models.CASCADE)
    opportunity_uuid = models.UUIDField()


class AdvisorRequestSettings(TimeStampedModel):
    project = models.OneToOneField(
        'project.Project',
        related_name='advisor_request_settings',
        on_delete=models.CASCADE)
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
    budgets = JSONField(blank=True, null=True)


class OpportunityTeamGroup(TimeStampedModel):
    team = models.OneToOneField(
        'team.Team',
        related_name='opportunity_group',
        on_delete=models.CASCADE)
    group_uuid = models.UUIDField(
        blank=True, null=True)

    @property
    def managers(self):
        return list(self.team.members) + list(self.team.project.head_coaches)
