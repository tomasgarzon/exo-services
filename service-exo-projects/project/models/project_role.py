from django.db import models

from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField

from utils.models import CreatedByMixin

from ..conf import settings


class ProjectRole(CreatedByMixin, TimeStampedModel):
    project = models.ForeignKey(
        'Project',
        related_name='project_roles',
        on_delete=models.CASCADE
    )
    order = models.IntegerField(default=0)
    code = models.CharField(
        max_length=3,
        blank=True, null=True)
    role = models.CharField(max_length=200)
    level = MultiSelectField(
        choices=settings.PROJECT_ROLE_LEVEL,
        default=settings.PROJECT_CH_ROLE_LEVEL_DEFAULT,
    )
    groups = MultiSelectField(
        choices=settings.PROJECT_CH_GROUP_CHOICES,
        blank=True, null=True,
    )
    default = models.BooleanField(default=False)
    exo_role = models.ForeignKey(
        'exo_role.ExoRole',
        on_delete=models.SET_NULL,
        blank=True, null=True)

    class Meta:
        ordering = ['project', 'role']
        unique_together = ['project', 'code']

    def __str__(self):
        return str(self.role)

    @property
    def is_participant_code(self):
        return self.code == settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT
