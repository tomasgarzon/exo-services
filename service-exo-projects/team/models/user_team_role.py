from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from ..managers.user_team_role import UserTeamRoleManager
from ..signals_define import user_team_role_activated


class UserTeamRole(CreatedByMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_team_roles',
        on_delete=models.CASCADE)
    team = models.ForeignKey(
        'team',
        related_name='user_team_roles',
        on_delete=models.CASCADE)
    team_role = models.ForeignKey(
        'ProjectTeamRole',
        related_name='user_team_roles',
        on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    objects = UserTeamRoleManager()

    class Meta:
        ordering = ['team_role__role']
        unique_together = ('user', 'team', 'team_role')

    def __str__(self):
        return '{} - {}'.format(self.user, self.team_role)

    @property
    def project(self):
        return self.team_role.project

    @property
    def role(self):
        return self.team_role.role

    def activate(self, user_from):
        self.active = True
        self.save(update_fields=['active', 'modified'])
        user_team_role_activated.send(
            sender=self.__class__,
            instance=self,
            user_from=user_from)

    def user_actions(self, user_from):
        users = self.team.user_team_roles.exists()
        if not users:
            return []
        actions = [
            settings.TEAM_CH_ACTION_USER_TEAM_UNSELECT
        ]
        if self.team_role.is_participant_code:
            if not self.active:
                actions.append(settings.TEAM_CH_ACTION_USER_TEAM_EDIT_PARTICIPANT)
            else:
                actions.append(settings.TEAM_CH_ACTION_USER_TEAM_EDIT_TEAMS)
        else:
            actions.append(settings.TEAM_CH_ACTION_USER_TEAM_EDIT_ROLES)
        actions.append(
            settings.TEAM_CH_ACTION_USER_TEAM_MOVE)
        return actions
