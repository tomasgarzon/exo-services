class ProjectMailMixin:

    def __init__(self, project):
        self.project = project

    def get_data(self):

        return {
            'name': self.project.name,
        }
