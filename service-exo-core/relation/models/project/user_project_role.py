from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError

from utils.mail import handlers

from ..role import Role
from ..mixins import InvitationPublicURLMixin
from ...conf import settings
from ...managers.project_user import ProjectUserRoleManager


class UserProjectRole(InvitationPublicURLMixin, Role):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='projects_member',
        on_delete=models.CASCADE)
    project = models.ForeignKey(
        'project.Project',
        related_name='users_roles',
        on_delete=models.CASCADE)
    exo_role = models.ForeignKey(
        'exo_role.ExORole',
        related_name='user_project_roles',
        blank=True, null=True,
        on_delete=models.CASCADE)
    exo_role_other_name = models.CharField(
        max_length=355, blank=True, null=True)
    certifications = GenericRelation(
        'certification.CertificationCredential')

    objects = ProjectUserRoleManager()

    _perms_activate = settings.PROJECT_PERMS_ADD_PROJECT
    _related_object = 'customer'

    class Meta:
        verbose_name_plural = 'User Projects Roles'
        verbose_name = 'User Project Role'
        permissions = settings.RELATION_ALL_PERMISSIONS

    def __str__(self):
        return str('%s - %s [%s]' % (
            self.user,
            self.project,
            self.exo_role.name,
        ))

    def customer(self):
        return self.project.customer

    @property
    def is_sprint(self):
        return not self.project.sprint

    @property
    def is_member(self):
        return self.exo_role.code == settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT

    @property
    def is_supervisor(self):
        return self.exo_role.code == settings.EXO_ROLE_CODE_SPRINT_OBSERVER

    @property
    def is_staff(self):
        return self.exo_role.code == settings.EXO_ROLE_CODE_SPRINT_OTHER

    @property
    def is_delivery_manager(self):
        return self.exo_role.code == settings.EXO_ROLE_CODE_DELIVERY_MANAGER

    @property
    def team(self):
        return self.project.team

    def send_notification(self, invitation):
        """
            Create notifications, for now only send an email
        """
        data = {}
        template_name = ''
        if self.is_member:
            try:
                team = self.user.teams.filter(project=self.project)[0]
            except IndexError:
                team = None
            if team:
                data = {
                    'team_name': team.name,
                    'project_name': self.project.name,
                    'project_type': self.project.type_verbose_name,
                    'public_url': self.project.get_frontend_index_url(self.user),
                }
                template_name = 'invitation_user_project'
        elif self.is_supervisor:
            data = {
                'project_name': self.project.name,
                'project_type': self.project.type_verbose_name,
                'public_url': self.project.get_frontend_index_url(self.user),
            }
            template_name = 'invitation_observer_project'

        if data:
            handlers.mail_handler.send_mail(
                template_name,
                recipients=[self.user.email],
                **data
            )

    def can_activate(self, user_from):
        """Activate this role"""
        perm_active_role = user_from.has_perm(settings.RELATION_ACTIVE_ROLE, self)
        user_in_organization = self.project.internal_organization \
            and user_from.has_perm(
                settings.CUSTOM_AUTH_ADMIN_ROLE,
                self.project.internal_organization)

        if not(perm_active_role or user_in_organization):
            raise ValidationError(
                "User doesn't allow to deactive this role: ({} given)".format(user_from))

        return True
