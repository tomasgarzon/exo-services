from .mixin import ProjectMailMixin

from auth_uuid.utils.user_wrapper import UserWrapper


class LocationChanged(ProjectMailMixin):
    def __init__(self, project, user):
        self.user = user
        super().__init__(project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)

        data.update({
            'location': self.project.location,
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'name': self.project.name,
            }
        })
        return data


class StepDateChanged(ProjectMailMixin):
    def __init__(self, step, user):
        self.user = user
        self.step = step
        super().__init__(step.project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)

        data.update({
            'start_date': self.step.start.strftime('%d-%m-%Y'),
            'name': self.step.name,
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'name': self.step.name,
                'start_date': self.step.start.strftime('%d-%m-%Y'),
            }
        })
        return data


class ProjectDateChanged(ProjectMailMixin):
    def __init__(self, project, user):
        self.user = user
        super().__init__(project)

    def get_data(self):
        data = super().get_data()

        user_wrapper = UserWrapper(user=self.user)

        data.update({
            'start_date': self.project.start.strftime('%d-%m-%Y'),
            'user_name': user_wrapper.get_full_name(),
            'email': user_wrapper.email,
            'public_url': self.project.url_zone(self.user),
            'subject_args': {
                'name': self.project.name,
                'start_date': self.project.start.strftime('%d-%m-%Y'),
            }
        })
        return data
