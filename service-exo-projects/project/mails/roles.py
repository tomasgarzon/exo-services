from .mixin import ProjectMailMixin

from auth_uuid.utils.user_wrapper import UserWrapper


class RoleChanged(ProjectMailMixin):
    def __init__(self, project, user):
        self.user = user
        super().__init__(project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)
        roles = self.user.user_project_roles.filter(
            project_role__project=self.project).values_list(
            'project_role__exo_role__name', flat=True)
        roles = ', '.join(list(roles))
        data.update({
            'roles': roles,
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'name': self.project.name,
                'roles': roles,
            }
        })
        return data


class UserAddedTeamChanged(ProjectMailMixin):
    def __init__(self, team, user):
        self.user = user
        self.team = team
        super().__init__(team.project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)
        roles = self.user.user_team_roles.filter(
            team=self.team).values_list(
            'team_role__role', flat=True)
        roles = ', '.join(list(roles))
        data.update({
            'roles': roles,
            'team_name': self.team.name,
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'team_name': self.team.name,
                'roles': roles,
            }
        })
        return data


class RoleRemoved(ProjectMailMixin):
    def __init__(self, project, roles, user):
        self.user = user
        self.roles = roles
        super().__init__(project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)
        data.update({
            'roles': self.roles,
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'name': self.project.name,
                'roles': self.roles,
            }
        })
        return data
