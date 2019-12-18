class ProjectException(Exception):
    def __init__(self, project, message):
        self.project = project
        self.message = message
        super().__init__(message)


class ProjectRemovedException(ProjectException):
    pass
