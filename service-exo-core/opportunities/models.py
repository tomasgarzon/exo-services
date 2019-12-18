from django.db import models
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel

from .conf import settings


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
        managers = [self.team.coach.user] + list(self.team.team_members.all())
        if self.team.project.project_manager:
            managers.append(self.team.project.project_manager.user)
        for user in self.team.project.delivery_managers:
            managers.append(user)
        return managers
