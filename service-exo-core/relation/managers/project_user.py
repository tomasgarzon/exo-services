from django.conf import settings

from invitation.models import Invitation

from .role import RoleManager
from ..queryset.project_user import ProjectUserQuerySet


class ProjectUserRoleManager(RoleManager):
    queryset_class = ProjectUserQuerySet

    def get_args_for_create(self, user, role):
        args = {
            'project': self.instance,
            'user': user,
            'exo_role': role,
        }
        return args

    def filter_by_project(self, project):
        return self.get_queryset().filter_by_project(project)

    def filter_by_exo_role(self, exo_role):
        return self.get_queryset().filter_by_exo_role(exo_role)

    def filter_by_exo_role_code(self, code):
        return self.get_queryset().filter_by_exo_role_code(code)

    def get_or_create_user(self, user_from, user, project, exo_role, status=None):
        if project.is_draft and exo_role.code != settings.EXO_ROLE_CODE_DELIVERY_MANAGER:
            status = settings.RELATION_ROLE_CH_INACTIVE
        else:
            status = settings.RELATION_ROLE_CH_ACTIVE

        user_role, created = self.get_or_create_role(user, exo_role, status)

        if user_role.is_active:
            invitation_status = settings.INVITATION_STATUS_CH_ACTIVE
        else:
            invitation_status = settings.INVITATION_STATUS_CH_PENDING

        if created:
            Invitation.objects.create_role_invitation(
                user_from=user_from,
                user_to=user_role.user,
                role=user_role,
                autosend=project.autosend(consultant=False),
                status=invitation_status,
            )
        if not user_role.user.password_updated and project.settings.launch['fix_password']:
            user = user_role.user
            user.set_password(project.settings.launch['fix_password'])
            user.save()

        return user_role, created

    def remove_user(self, user, exo_role):
        self.get_queryset().filter_by_user(user).filter_by_exo_role(exo_role).delete()
