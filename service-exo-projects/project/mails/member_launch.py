from .mixin import ProjectMailMixin

from auth_uuid.utils.user_wrapper import UserWrapper


class MemberLaunch(ProjectMailMixin):
    def __init__(self, project, user):
        self.user = user
        super().__init__(project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)

        roles = list(self.user.user_project_roles.filter(
            project_role__project=self.project).values_list(
            'project_role__exo_role__name', flat=True))
        roles = ', '.join(roles)
        data.update({
            'roles': roles,
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'start_date': self.project.start.strftime('%d-%m-%Y'),
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'roles': roles,
                'name': self.project.name,
            }
        })
        return data
