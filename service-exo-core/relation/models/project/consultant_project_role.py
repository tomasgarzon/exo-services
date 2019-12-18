from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.conf import settings

from utils.mail import handlers
from utils.mixins import ModelDiffMixin

from ...managers.consultant_project import ConsultantProjectRoleManager
from ..role import Role
from ..mixins import InvitationPublicURLMixin


class ConsultantProjectRole(ModelDiffMixin, InvitationPublicURLMixin, Role):

    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='roles',
        blank=True,
        on_delete=models.CASCADE)
    project = models.ForeignKey(
        'project.Project',
        related_name='consultants_roles',
        blank=True,
        on_delete=models.CASCADE)
    exo_role = models.ForeignKey(
        'exo_role.ExORole',
        related_name='consultants_roles',
        blank=True, null=True,
        on_delete=models.CASCADE)
    exo_role_other_name = models.CharField(
        max_length=355, blank=True, null=True)
    interactions = GenericRelation(
        'ratings.Interaction',
        related_query_name='interactions')

    objects = ConsultantProjectRoleManager()

    _perms_activate = settings.PROJECT_PERMS_ADD_PROJECT
    _related_object = 'customer'

    class Meta:
        verbose_name_plural = 'Consultant Project Roles'
        verbose_name = 'Consultant Project Role'
        permissions = settings.RELATION_ALL_PERMISSIONS

    def __str__(self):
        return str('%s %s [%s]' % (
            self.consultant, self.project,
            self.exo_role.name,
        ))

    def customer(self):
        return self.project.customer

    def get_data_email(self, invitation):
        # we only send email to coach and advisors
        data = {}

        if self.has_team_manager_perms:
            try:
                team = self.consultant.teams_coach.filter(project=self.project)[0]
            except IndexError:
                # if user hasn't team, don't send email
                return None
            data = {
                'user': team.created_by.short_name,
                'team_name': team.name,
                'project_name': self.project.name,
                'is_coach': self.has_team_manager_perms,
                'relation_name': self.label,
            }

        if self.exo_role.code == settings.EXO_ROLE_CODE_ADVISOR:
            data = {
                'user': self.project.project_manager.user.short_name,
                'project_name': self.project.name,
                'is_coach': self.has_team_manager_perms,
                'relation_name': self.label,
            }
        return data

    def send_notification(self, invitation):
        """
            Create notifications, for now only send an email
        """
        data = self.get_data_email(invitation)
        if data:
            handlers.mail_handler.send_mail(
                'invitation_consultant_project',
                recipients=[self.consultant.user.email],
                subject_args={
                    'relation_name': data['relation_name'],
                    'is_coach': self.has_team_manager_perms,
                },
                public_url=settings.FRONTEND_CIRCLES_PAGE,
                **data
            )

    @property
    def has_manager_perms(self):
        roles = self.project.customize_roles
        for rol_code in roles.get('manager'):
            if rol_code == self.exo_role.code:
                return True
        return False

    @property
    def has_team_manager_perms(self):
        roles = self.project.customize.get('roles')
        for rol_code in roles.get('team_manager'):
            if rol_code == self.exo_role.code:
                return True
        return False

    @property
    def can_be_deleted(self):
        # For now, we can't remove a consultant if he is a team's coach and he hasn't any other roles in this project
        if self.project.teams.filter(coach=self.consultant) \
                and not self.project.consultants_roles.filter(
                consultant=self.consultant,
        ).exclude(id=self.id).actives_only().exists():
            return False
        return True

    @property
    def label(self):
        return self.exo_role.name

    @property
    def rating(self):
        try:
            return self.interactions.first().rating
        except AttributeError:
            return None

    def can_activate(self, user_from):
        """Activate this role"""
        perm_active_role = user_from.has_perm(settings.RELATION_ACTIVE_ROLE, self)
        user_in_organization = self.project.internal_organization\
            and user_from.has_perm(
                settings.CUSTOM_AUTH_ADMIN_ROLE,
                self.project.internal_organization)
        if not(perm_active_role or user_in_organization):
            raise ValidationError(
                "User doesn't allow to deactive this role: ({} given)".format(user_from),
            )
        return True

    def change_visibility(self):
        self.visible = not self.visible
        self.save(update_fields=['visible'])

    @property
    def user(self):
        return self.consultant.user
