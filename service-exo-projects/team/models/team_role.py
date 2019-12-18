from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField
from exo_role.models import ExORole

from utils.models import CreatedByMixin


class ProjectTeamRole(CreatedByMixin, TimeStampedModel):
    project = models.ForeignKey(
        'project.Project',
        related_name='team_roles',
        on_delete=models.CASCADE
    )
    role = models.CharField(max_length=200)
    code = models.CharField(
        max_length=3,
        blank=True, null=True)
    level = MultiSelectField(
        max_length=20,
        choices=settings.PROJECT_ROLE_LEVEL,
        default=settings.PROJECT_CH_ROLE_LEVEL_DEFAULT,
    )
    default = models.BooleanField(default=False)

    class Meta:
        ordering = ['level', 'role']
        unique_together = ['project', 'code']

    def __str__(self):
        return str(self.role)

    @property
    def is_participant_code(self):
        return self.code == settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT

    @property
    def exo_role(self):
        return ExORole.objects.get(code=self.code)
