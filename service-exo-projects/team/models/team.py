import uuid

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.auth import get_user_model

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin
from utils.permissions import PermissionManagerMixin

from ..conf import settings
from ..managers.team import TeamManager
from .team_member import TeamMemberManager
from .mixins import TeamPermissions
import reversion


@reversion.register()
class Team(
        PermissionManagerMixin,
        TeamPermissions,
        CreatedByMixin,
        TimeStampedModel):
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(
        'project.Project',
        related_name='teams',
        on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    stream = models.ForeignKey(
        'utils.Stream',
        on_delete=models.CASCADE,
        related_name='teams',
        blank=True, null=True)
    permissions = GenericRelation(
        'guardian.UserObjectPermission',
        content_type_field='content_type',
        object_id_field='object_pk',
        related_query_name='teams')
    image = models.CharField(
        max_length=200,
        blank=True, null=True)

    objects = TeamManager()

    SEARCHEABLE_FIELDS = ['name']

    class Meta:
        permissions = settings.TEAM_ALL_PERMISSIONS
        ordering = ['name']

    def __str__(self):
        return str('%s ' % self.name)

    @property
    def members(self):
        return get_user_model().objects.filter(
            user_team_roles__team=self
        ).distinct()

    @property
    def participants(self):
        return self.user_team_roles.filter(team_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).users()

    @property
    def coaches(self):
        return self.user_team_roles.filter(team_role__code=settings.EXO_ROLE_CODE_SPRINT_COACH).users()

    def user_actions(self, user_from):
        if self.project.created_by != user_from and not user_from.is_superuser:
            return []
        actions = [
            settings.TEAM_CH_ACTION_EDIT,
            settings.TEAM_CH_ACTION_DELETE
        ]
        if self.project.users_without_team().exists():
            actions.append(settings.TEAM_CH_ACTION_PARTICIPANTS)
        return actions

    @property
    def member_manager(self):
        if not hasattr(self, '_members'):
            self._members = TeamMemberManager(self)
        return self._members
