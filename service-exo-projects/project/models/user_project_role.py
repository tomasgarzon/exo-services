from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel
from utils.models import CreatedByMixin
from utils.permissions.objects import get_team_for_user

from ..managers.user_project_role import UserProjectRoleManager
from ..signals_define import user_project_role_activated


class UserProjectRole(CreatedByMixin, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_project_roles',
        on_delete=models.CASCADE)
    project_role = models.ForeignKey(
        'ProjectRole',
        related_name='user_project_roles',
        on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    objects = UserProjectRoleManager()

    class Meta:
        ordering = ['project_role__role']
        unique_together = ('user', 'project_role')

    def __str__(self):
        return '{} - {}'.format(self.user, self.project_role)

    def get_customer(self):
        return self.project.customer

    @property
    def project(self):
        return self.project_role.project

    @property
    def role(self):
        return self.project_role.role

    @property
    def exo_role(self):
        return self.project_role.exo_role

    def activate(self, user_from):
        self.active = True
        self.save(update_fields=['active', 'modified'])
        user_project_role_activated.send(
            sender=self.__class__,
            instance=self,
            user_from=user_from)

    @property
    def teams(self):
        return self.user.user_team_roles.filter(
            team__project=self.project_role.project).distinct()

    @property
    def url(self):
        teams = get_team_for_user(self.project, self.user)
        if not teams:
            return settings.PROJECT_URL_PROFILE.format(self.project.id)
        team = teams.first()
        try:
            current_step = self.project.steps.filter(
                status=settings.PROJECT_CH_STATUS_STEP_CURRENT).get()
        except Exception:
            current_step = self.project.current_step()

        return settings.PROJECT_URL_ZONE.format(
            self.project.id,
            team.id,
            current_step.id)
