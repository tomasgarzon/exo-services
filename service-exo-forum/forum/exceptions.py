class CategoryException(Exception):
    def __init__(self, category, message):
        self.category = category
        self.message = message
        super().__init__(message)


class CategoryRemovedException(CategoryException):
    pass


class CategoryPermissionException(CategoryException):
    pass
