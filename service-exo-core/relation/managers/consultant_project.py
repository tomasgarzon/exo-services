from django.conf import settings

from invitation.models import Invitation

from .role import RoleManager
from ..queryset.consultant_project import ConsultantProjectQuerySet


class ConsultantProjectRoleManager(RoleManager):
    queryset_class = ConsultantProjectQuerySet

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_user(self, user):
        return self.get_queryset().filter_by_user(user)

    def filter_by_exo_role(self, exo_role):
        return self.get_queryset().filter_by_exo_role(exo_role)

    def filter_by_exo_role_code(self, code):
        return self.get_queryset().filter_by_exo_role_code(code)

    def consultants(self):
        return self.get_queryset().consultants()

    def get_args_for_create(self, user, role):
        # revisar
        args = {
            'consultant': self.instance,
            'user': user,
            'exo_role': role,
        }
        return args

    def _get_consultant(self, consultant, project, exo_role):
        """
        Get the ConsultantProjectRole object for a Consultant
        and a Role if exist
        """
        return self.get_queryset().get(
            consultant=consultant,
            project=project,
            exo_role=exo_role,
        )

    def get_consultants_by_role(self, exo_role):
        """
        Return the Consultants with a concrete Role for
        this project
        """
        return self.get_queryset().filter_by_exo_role(exo_role)

    def get_or_create_consultant(
            self, user_from, consultant, project,
            exo_role, exo_role_other_name=None, status=None):
        """
        If we call to this method the ConsultantProjectRole object
        will be activated automatically and the system will no send
        any kind of invitation for this Role and Project
        """

        if not status:
            if project.is_draft:
                status = settings.RELATION_ROLE_CH_INACTIVE
            else:
                status = settings.RELATION_ROLE_CH_ACTIVE
        created = False
        try:
            consultant_coach = self._get_consultant(
                consultant=consultant,
                project=project,
                exo_role=exo_role,
            )
        except self.model.DoesNotExist:
            consultant_coach = self.create_consultant(
                user_from=user_from,
                project=project,
                consultant=consultant,
                exo_role=exo_role,
                exo_role_other_name=exo_role_other_name,
                status=status,
            )
            created = True

        return consultant_coach, created

    def create_consultant(
            self, user_from, project, consultant,
            exo_role, exo_role_other_name=None, status=None):
        """
        Creates a Consultant with a Role for the Project
        """
        consultant_role = self.model(
            project=project,
            consultant=consultant,
            exo_role=exo_role,
        )

        if status:
            consultant_role.status = status

        if exo_role_other_name:
            consultant_role.exo_role_other_name = exo_role_other_name

        consultant_role.save()

        if consultant_role.is_active:
            invitation_status = settings.INVITATION_STATUS_CH_ACTIVE
        else:
            invitation_status = settings.INVITATION_STATUS_CH_PENDING

        Invitation.objects.create_role_invitation(
            user_from=user_from,
            user_to=consultant_role.consultant.user,
            role=consultant_role,
            autosend=consultant_role.project.autosend(consultant=True),
            status=invitation_status,
        )
        return consultant_role

    def get_team_manager_consultants(self, project):
        roles = project.customize.get('roles').get('team_manager')
        return self.get_queryset().filter(
            exo_role__code__in=roles,
            project=project)

    def get_project_manager_consultants(self, project):
        roles = project.customize.get('roles').get('manager')
        return self.get_queryset().filter(
            exo_role__code__in=roles,
            project=project)
