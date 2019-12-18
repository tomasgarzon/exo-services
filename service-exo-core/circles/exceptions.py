class CircleException(Exception):
    def __init__(self, circle, message):
        self.circle = circle
        self.message = message
        super().__init__(message)


class CircleRemovedException(CircleException):
    pass


class CirclePermissionException(CircleException):
    pass
